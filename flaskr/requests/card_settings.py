from cerberus import Validator
from flaskr import db
from flaskr.models.field import Field
from flaskr.models.installation_card_settings import InstallationCardSettings


def text_options_to_json(text):
    json = {}

    for line in text.splitlines():
        pos_index = line.find('=')
        if pos_index == -1:
            break

        line_key = line[0:pos_index]
        line_value = line[(pos_index + 1):]
        if line_key and line_value:
            json[line_key] = line_value

    return json


# Update card settings
def update_card_settings(params, request_data):
    vld = Validator({
        'amountEnabled': {'type': 'boolean', 'required': True},
        'currency': {'type': 'string', 'required': True},
        'fields': {'type': 'list', 'required': True}
    })
    is_valid = vld.validate(params)
    if not is_valid:
        return {'res': 'err', 'message': 'Invalid params', 'errors': vld.errors}

    card_settings = InstallationCardSettings.query \
        .filter_by(nepkit_installation_id=request_data['installation_id']) \
        .first()

    card_settings.amount_enabled = params.get('amountEnabled')
    card_settings.currency = params.get('currency')

    # Set fields
    if params.get('fields'):
        i = 0
        removed_field_ids = []

        # Get current fields
        exist_fields = Field.query \
            .filter_by(nepkit_installation_id=request_data['installation_id']) \
            .order_by(Field.index.asc()) \
            .all()
        for exist_field in exist_fields:
            removed_field_ids.append(exist_field.id)

        for field in params['fields']:
            if field.get('name') and field.get('valueType'):
                if field.get('id'):
                    # Update exist field
                    exist_field = Field.query \
                        .filter_by(id=field['id'],
                                   nepkit_installation_id=request_data['installation_id']) \
                        .first()
                    exist_field.index = i
                    exist_field.name = field['name']
                    exist_field.value_type = field['valueType']
                    exist_field.choice_options = text_options_to_json(field['choiceOptions']) if field.get('choiceOptions') else None
                    exist_field.board_visibility = field['boardVisibility']

                    removed_field_ids.remove(exist_field.id)
                else:
                    # Create new field
                    new_field = Field()
                    new_field.index = i
                    new_field.name = field['name']
                    new_field.value_type = field['valueType']
                    new_field.choice_options = text_options_to_json(field['choiceOptions']) if field.get('choiceOptions') else None
                    new_field.board_visibility = field['boardVisibility']
                    new_field.nepkit_installation_id = request_data['installation_id']

                    db.session.add(new_field)
            i += 1

        if len(removed_field_ids) > 0:
            Field.query \
                .filter(Field.id.in_(removed_field_ids, )) \
                .delete(synchronize_session=False)

    db.session.commit()

    return {
        'res': 'ok'
    }
