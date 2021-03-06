from flaskr.extensions.tilda import TildaExtension
from flaskr.extensions.mottor import MottorExtension
from flaskr.extensions.wix import WixExtension
from flaskr.extensions.wordpress import WordpressExtension

extensions_map = {
    'tilda': TildaExtension,
    'mottor': MottorExtension,
    'wix': WixExtension,
    'wordpress': WordpressExtension
}


# Get extension by id
def get_extension_by_id(id):
    for extension in list(extensions_map.values()):
        print('id', extension.id, id)
        if int(extension.id) == int(id):
            return extension

    return None
