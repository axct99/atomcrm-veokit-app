from flask_babel import _
from sqlalchemy.dialects.postgresql import JSONB
from flaskr import db
import enum
from sqlalchemy import Integer, Enum, Column


# Field type
class FieldType(enum.Enum):
    string = 10
    # string_phone = 11
    # string_email = 12
    long_string = 20
    number = 30
    boolean = 40
    date = 50
    choice = 60


# Field board visibility
class FieldBoardVisibility(enum.Enum):
    none = 1
    title = 2
    subtitle = 3


# Field
class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), nullable=False)

    value_type = Column(Enum(FieldType), nullable=False, server_default='string')
    board_visibility = Column(Enum(FieldBoardVisibility), nullable=False, server_default='none')

    choice_options = db.Column(JSONB, nullable=True)

    index = db.Column(db.Integer, default=0, nullable=False)

    nepkit_installation_id = db.Column(db.Integer, nullable=False, index=True)


def get_field_types():
    return (
        (1, 'string', _('m_status_getFieldTypes_string')),
        (2, 'long_string', _('m_status_getFieldTypes_longString')),
        (3, 'number', _('m_status_getFieldTypes_number')),
        (4, 'boolean', _('m_status_getFieldTypes_boolean')),
        (5, 'date', _('m_status_getFieldTypes_date')),
        (6, 'choice', _('m_status_getFieldTypes_choice')),
        # (7, 'file', _('m_status_getFieldTypes_file'))
    )


def get_board_visibility():
    return (
        (1, 'none', _('m_status_getBoardVisibility_none')),
        (2, 'title', _('m_status_getBoardVisibility_title')),
        (3, 'subtitle', _('m_status_getBoardVisibility_subtitle'))
    )
