from datetime import timedelta

from flaskr import db
from flaskr.views.view import View
from flaskr.models.lead import Lead
from flaskr.models.status import Status, get_hex_by_color


# Page: Pipeline
class Pipeline(View):
    meta = {
        'name': 'Leads'
    }

    leads = []
    statuses = []

    def before(self, params, request_data):
        statuses_q = db.session.execute("""  
            SELECT 
                s.*,
                (SELECT COUNT(*) FROM public.lead AS l WHERE l.status_id = s.id AND l.archived = false) AS lead_count
            FROM 
                public.status AS s
            WHERE
                s.veokit_installation_id = :installation_id
            ORDER BY 
                s.index""", {
            'installation_id': request_data['installation_id']
        })

        self.statuses = []
        for status in statuses_q:
            leads_q = Lead.get_with_filter(installation_id=request_data['installation_id'],
                                           status_id=status['id'],
                                           search=params.get('search'),
                                           offset=0,
                                           limit=10,
                                           period_from=params.get('periodFrom'),
                                           period_to=params.get('periodTo'))

            status_leads = []
            status_lead_total = 0

            for lead in leads_q:
                if status_lead_total == 0:
                    status_lead_total = lead.total

                status_leads.append({
                    'id': lead.id,
                    'status_id': lead.status_id,
                    'archived': lead.archived,
                    'add_date': (lead.add_date + timedelta(minutes=request_data['timezone_offset'])).strftime('%Y-%m-%d %H:%M:%S'),
                    'fields': Lead.get_fields(lead.id),
                    'tags': Lead.get_tags(lead.id)
                })

            self.statuses.append({
                'id': status['id'],
                'name': status['name'],
                'lead_count': status_lead_total,
                'color': status['color'],
                'leads': status_leads
            })

    def get_header(self, params, request_data):
        return {
            'title': self.meta.get('name'),
            'actions': [
                {
                    '_com': 'Button',
                    'icon': 'infoCircle',
                    'toWindow': 'searchInfo'
                },
                {
                    '_com': 'Field.DatePicker',
                    'range': True,
                    'allowClear': True,
                    'format': 'YYYY.MM.DD',
                    'onChange': 'onChangePeriod'
                }
            ],
            'search': {
                'placeholder': 'Search...',
                'onSearch': 'onSearchLeads'
            }
        }

    def get_schema(self, params, request_data):
        board_columns = []

        for status in self.statuses:
            board_column_items = []

            for lead in status['leads']:
                board_column_items.append(get_lead_component(lead))

            board_columns.append({
                'key': status['id'],
                'title': status['name'],
                'color': get_hex_by_color(status['color']),
                'items': board_column_items,
                'showAdd': False if (
                            params.get('search') or params.get('periodFrom') or params.get('periodTo')) else True,
                'onAdd': 'addLead',
                'total': status['lead_count'],
                'loadLimit': 10,
                'onLoad': ['loadLeads', {
                    'statusId': status['id'],
                    'addToEnd': True
                }]
            })

        return [
            {
                '_com': 'Board',
                '_id': 'leadsBoard',
                # 'draggable': True,
                'draggableBetweenColumns': True,
                'onDrag': 'onDragLead',
                'columns': board_columns
            }
        ]

    def get_methods(self, params, request_data):
        return {
            # Add lead to status
            'addLead':
                """(app, params, event) => {
                    const { columnKey, columnIndex } = event
                    const page = app.getView()
                    const board = page.getCom('leadsBoard')
                    const boardColumns = board.getAttr('columns')

                    // Set loading to add button
                    boardColumns[columnIndex].addLoading = true
                    board.setAttr('columns', boardColumns)

                    app
                        .sendReq('createLead', {
                            statusId: columnKey
                        })
                        .then(result => {
                            if (result.res === 'ok') {
                                // Update leads in column
                                app
                                    .sendReq('getLeadComponents', {
                                        statusId: columnKey,
                                        offset: 0,
                                        limit: 10
                                    })
                                    .then(result => {
                                        // Unset loading to add button
                                        boardColumns[columnIndex].addLoading = false
                                        board.setAttr('columns', boardColumns)

                                        if (result.res == 'ok') {
                                            const { leadComponents, leadTotal } = result

                                            // Set total and set/append items
                                            boardColumns[columnIndex].total = leadTotal
                                            boardColumns[columnIndex].items = leadComponents

                                            board.setAttr('columns', boardColumns)
                                        }
                                    })
                            }
                        })
                }""",

            # Load leads by status
            'loadLeads':
                """(app, params) => {
                    const { statusId, addToEnd=false } = params
                    const page = app.getView()
                    const board = page.getCom('leadsBoard')
                    const boardColumns = board.getAttr('columns')
                    const columnIndex = boardColumns.findIndex(c => c.key == statusId)

                    // Set loading to load button
                    boardColumns[columnIndex].loading = true
                    board.setAttr('columns', boardColumns)

                    app
                        .sendReq('getLeadComponents', {
                            statusId,
                            offset: addToEnd ? boardColumns[columnIndex].items.length : 0,
                            limit: addToEnd ? 10 : boardColumns[columnIndex].items.length,
                            search: '""" + str(params['search'] if params.get('search') else '') + """',
                            periodFrom: '""" + str(params['periodFrom'] if params.get('periodFrom') else '') + """',
                            periodTo: '""" + str(params['periodFrom'] if params.get('periodTo') else '') + """'
                        })
                        .then(result => {
                            // Unset loading to load button
                            boardColumns[columnIndex].loading = false
                            board.setAttr('columns', boardColumns)

                            if (result.res === 'ok') {
                                const { leadComponents, leadTotal } = result

                                // Set total and set/append items
                                boardColumns[columnIndex].total = leadTotal
                                boardColumns[columnIndex].items = !addToEnd ? leadComponents : [
                                    ...boardColumns[columnIndex].items,
                                    ...leadComponents
                                ]

                                board.setAttr('columns', boardColumns)
                            }
                        })
                }""",

            # Drag lead between statuses
            'onDragLead':
                """(app, params, event) => {
                    const { key, oldColumnIndex, newColumnIndex, newColumnKey, oldItemIndex, newItemIndex } = event
                    const page = app.getView()
                    const board = page.getCom('leadsBoard')
                    const boardColumns = board.getAttr('columns')

                    // Get item from old column
                    const item = boardColumns[oldColumnIndex].items[oldItemIndex]
                    // Add item new column
                    boardColumns[newColumnIndex].items.splice(newItemIndex, 0, item)
                    // Remove item from column
                    boardColumns[oldColumnIndex].items.splice(oldItemIndex, 1)

                    // Set loading to both columns
                    boardColumns[newColumnIndex].loading = true
                    boardColumns[oldColumnIndex].loading = true

                    // Change totals to both columns
                    boardColumns[newColumnIndex].total++
                    boardColumns[oldColumnIndex].total--

                    // Update columns on board
                    board.setAttr('columns', boardColumns)

                    app
                        .sendReq('updateLeadStatus', {
                            id: key,
                            statusId: newColumnKey
                        })
                        .then(result => {
                            // Unset loading to both columns
                            boardColumns[newColumnIndex].loading = false
                            boardColumns[oldColumnIndex].loading = false
                            board.setAttr('columns', boardColumns)
                        })
                }""",

            # On search
            'onSearchLeads': """(app, params, event) => {
                    app.getPage().to({
                        search: event.value,
                        periodFrom: '""" + str(params['periodFrom'] if params.get('periodFrom') else '') + """',
                        periodTo: '""" + str(params['periodFrom'] if params.get('periodTo') else '') + """'
                    })
                }""",

            # On change period
            'onChangePeriod': """(app, params, event) => {
                    app.getPage().to({ 
                        search: '""" + str(params['search'] if params.get('search') else '') + """',
                        periodFrom: event.value[0],
                        periodTo: event.value[1] 
                    })
                }"""
        }


# Get lead component
def get_lead_component(lead):
    title = ''
    description = []
    for field in lead['fields']:
        if field['field_value_type'] in ('number', 'string'):
            if field['field_as_title'] and field['value']:
                title += field['value'] + ' '
            elif field['field_primary'] and field['value']:
                description.append(field['value'])
    title = title.strip()

    return {
        'key': lead['id'],
        'columnKey': lead['status_id'],
        'title': title if title else 'No name',
        'description': ';'.join(description) if len(description) > 0 else 'Empty lead',
        'extra': 'Archived' if lead['archived'] else Lead.get_regular_date(lead['add_date']),
        'addDate': lead['id'],
        'toWindow': ['updateLead', {
            'id': lead['id']
        }]
    }
