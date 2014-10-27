#!/usr/bin/env python
# coding: utf8

# SQLEDITABLE plugin for web2py flamework
# Copyrighted by Hitoshi Kato <hi21alt-gl@yashoo.co.jp>
# License: LGPLv3

from gluon import *
from gluon.html import BUTTON
from gluon.utils import web2py_uuid, simple_hash
from gluon.storage import Storage
from os import urandom

FORMKEY_STRING                  = '_formkey[%s]'
FORMNAME                        = 'ajaxform'
TABLEHASH_STRING                = '_tablehash[%s]'

FORMKEY_ID                      = 'formkey'
FORMNAME_ID                     = 'formname'
EDITABLE_ID                     = 'editable'
AJAX_BUTTON_ID                  = 'ajax_btn'
ID_FORMAT                       = '%(row)d_%(field)s'
CELL_ID_FORMAT                  = 'cell_' + ID_FORMAT +'_'
PARENT_ID_FORMAT                = 'parent_' + ID_FORMAT +'_'
DELETABLE_ID_FORMAT             = 'd(%(row)d)'
KEY_ID_FORMAT                   = 'k(%(row)d)'
KEY_ID_TAG_ATTR                 = '_' + 'data-keyid'

MSG_SUCCESS_CLASS               = 'message_success'
MSG_FAILURE_CLASS               = 'message_failure'
MSG_ERROR_ID                    = 'message_error'
MSG_ERROR_CLASS                 = 'error'
PROCESS_DIALOG_CLASS            = 'message_process'
FIELD_CLASS_PREFIX              = '__FIELD_'
DELETABLE_CLASS                 = '__DELETABLE_'
CELL_ERROR_CLASS                = 'error'
FIELD_DATE_CLASS                = 'date'
FIELD_TIME_CLASS                = 'time'
FIELD_DATETIME_CLASS            = 'datetime'
FIELD_SELECT_CLASS              = 'select'
NO_EDIT_CLASS                   = 'noedit'
FIRST_CELL_CLASS                = 'first_cell'
CLASS_PREFIX_FOR_MOBILE         = 'm'

DEFAULT_BUTTON_VALUE            = 'OK'
LINENO_LABEL                    = '#'
DELETABLE_LABEL                 = 'Del'
MSG_PROCESS_DIALOG              = 'in process'
DATE_FORMAT                     = 'yyyy-mm-dd'
SELECTBOX_DEFALUT_LABEL         = '---'

NEWRECORD_FLAG_FIELD            = '__newrecord__'
DELETE_FLAG_FIELD               = '__delete__'
NOTCHANGED_FLAG_FIELD           = '__notchanged__'
STORED_KEY_VALUE                = '__stored_key__'

TABLE_HASH_AVAILABLE            = True
RECORD_HASH_AVAILABLE           = True
RECORD_HASH_FIELD               = '__rechash__'
RECORD_HASH_TAG_ATTR            = '_' + 'data-rechash'
INPUT_HASH_FIELD                = '__inphash__'
INPUT_HASH_TAG_ATTR             = '_' + 'data-inphash'
DUMMY_RECORD_HASH_VALUE         = 'DUMMY'
MSG_RECORD_HASH_CHANGED         = 'record has been changed'
MSG_RECORD_HASH_DELETED         = 'record has been deleted'
HASH_ALGORITHM                  = 'md5'
HASH_SALT_LENGTH                = 8

class FieldInfo(object):
    def __init__(self, field, key_fields):
        self.field = field
        self.key_fields = key_fields

    def __getattr__(self, attr):
        if attr == 'name':
            return self.field['field']
        if attr in ('readable', 'writable'):
            return self.check_status(attr)
        if attr == 'label':
            if attr in self.field:
                return self.field[attr]
            elif 'field' in self.field:
                return self.field['field']
            return None
        if attr == 'default':
            if attr in self.field:
                return self.field[attr]
            return ''
        if attr in self.field:
            return self.field[attr]
        return None

    def __getitem__(self, field):
        return self.__getattr__(field)

    def __repr__(self):
      return str(self.field)
  
    def is_key(self):
        if self.field['field'] in self.key_fields:
            return True
        return False

    def check_status(self, attr):
        if attr in self.field and self.field[attr] is True:
            return True
        elif not attr in self.field:
            return True
        return False

    def has_attr(self, attr):
        if '.' in attr:
            attr = attr.split('.')
        else:
            attr = [attr]
        status = True
        target = self.field
        for p in attr:
            if p in target:
                target = target[p]
            else:
                status = False
        return status

class Header(object):
    def __init__(self, header, key_fields=[]):
        self.header = header
        self.fields = [f['field'] for f in self.header]
        self.key_fields = key_fields

    def __getattr__(self, field):
        if field in self.fields:
            return FieldInfo(self.header[self.fields.index(field)],
                                                                self.key_fields)
        else:
            return None
    
    def __getitem__(self, field):
        return self.__getattr__(field)

    def __repr__(self):
      return str(self.fields)

    def all(self):
        for f in self.fields:
            yield self.__getattr__(f)

    def readable(self):
        for f in self.fields:
            if self.__getattr__(f).readable is True:
                yield self.__getattr__(f)

    def writable(self):
        for f in self.fields:
            if self.__getattr__(f).writable is True:
                yield self.__getattr__(f)

    def key(self):
        for k in self.key_fields:
            yield self.__getattr__(k)

    def key_list(self):
        return [k for k in self.key_fields]

    def has_attr(self, attr):
        return attr in self.fields

class Record(object):
    def __init__(self, record, header, key_fields=[]):
        self.__dict__['record'] = record
        if not isinstance(header, Header):
            header = Header(header, key_fields)
        self.__dict__['header'] = header

    def __getattr__(self, field):
        if not field in self.header.fields:
            if field in self.record:
                return self.record[field]
            else:
                return None
        f = self.header[field]
        return self.__value(f)
    
    def __getitem__(self, field):
        return self.__getattr__(field)

    def __setattr__(self, field, value):
        self.record[field] = value

    def __setitem__(self, field, value):
        self.record[field] = value
        
    def __delitem__(self, field):
        del self.record[field]
        
    def __repr__(self):
      return str(self.record)

    def all(self):
        for f in self.header.all():
            yield f, self.__value(f)

    def readable(self):
        for f in self.header.readable():
            yield f, self.__value(f)

    def writable(self):
        for f in self.header.writable():
            yield f, self.__value(f)

    def __value(self, f):
        if f.name in self.record:
            value = self.record[f.name] 
            if value == '':
                return value
            if f.type == 'integer':
                value = value if value else 0
                try:
                    value = int(value)
                except:
                    pass
                return value
            if f.type == 'number':
                value = value if value else 0
                try:
                    value = float(value)
                except:
                    pass
                return value
            if f.type == 'time':
                if isinstance(value,str):
                    ls = value.split(':')
                    while range(3-len(ls)):
                        ls.append('00')
                    return ':'.join(ls)
            return value 
        return None

    def key_value(self):
        for f in self.header.key():
            if self.has_field(STORED_KEY_VALUE):
                yield f, self.record[STORED_KEY_VALUE][f.name]
            else:
                yield f, self.__value(f)

    def key_list(self):
        return self.header.key_list()

    def has_field(self, field):
        return field in self.record
    
    def as_dict(self):
        return self.record

class RecordArray(object):
    def __init__(self, array, header, key_fields=[]):
        self.array = array
        if not isinstance(header, Header):
            header = Header(header, key_fields)
        self.header = header

    def __iter__(self):
        for r in self.array:
            yield Record(r, self.header)

    def __len__(self):
        return len(self.array)

    def __getitem__(self, index):
        return Record(self.array[index], self.header)

    def append(self, value):
        if not isinstance(value, Record):
            raise TypeError('value mast be a Record object.')
        self.array.append(value.as_dict())

class EDITABLE(FORM):
    '''
        header: list of header info.
         [{'field': 'name1', 'label': 'test', 'type':'number', 'readable': True, 
                    'writable':True}, {'field': 'name2'}, {..}]

         - field: field name
         
             option dict
             - 'label': field label
             - 'type': integer/number/string/boolean/date/time 
                                                                default='string'
             - 'range': [minimum, maximum] (range of value)
             - 'length': [minimum, maximum] (size of value)
             - 'inset':{'multiple':True/False, 'zero': value, 'theset':[value1,value2,.......]}
             - 'readable': True/False                           default=True
             - 'writable': True/False                           default=True
             - 'default': field value                           default=0 or ''
        
        record : dict of one record
         {'field1':value1, 'field1':value2, ....., '__rechash__':hash}

        records : list of record
         [{record1}, {record2}, .....]
    '''

    def __init__(self, record, header, maxrow=None, lineno=True,
                 url=None, validate_js=True, vertical=True, deletable=False, 
                 oninit=None, **kwargs):

        self.editable_id = EDITABLE_ID

        if not self.is_ajax():
            if record and callable(record):
                record = record()
                
            if record and isinstance(record, (list, tuple)) and \
                                                isinstance(record[0] , dict):
                self.record = RecordArrey(record, header) 
            elif record:
                self.record = record
            else:
                self.record = None
            
            self.url = url if url else URL() 
            self.validate_js = validate_js
            # self.language = self.set_language()
            
            self.formname_id = FORMNAME_ID
            self.table_class = 'table table-bordered'

            self.lineno = lineno
            self.lineno_label = current.T(LINENO_LABEL)
            self.deleteable_label = current.T(DELETABLE_LABEL)
            self.maxrow = maxrow

            self.ajax_button_id = AJAX_BUTTON_ID
            self.ajax_button_value = current.T(DEFAULT_BUTTON_VALUE)
            self.ajax_button_class = 'btn btn-primary btn-lg'
            self.ajax_button_style = 'padding:10px 20px'

            self.touch_device = kwargs.get('touch_device', 'Auto')
            if self.touch_device == 'Auto':
                self.touch_device = self.is_touch_device()
            if self.touch_device:
                class_prefix_mobile = CLASS_PREFIX_FOR_MOBILE
            else:
                class_prefix_mobile = ''
            self.field_date_class = class_prefix_mobile+FIELD_DATE_CLASS
            self.field_time_class = class_prefix_mobile+FIELD_TIME_CLASS
            self.field_datetime_class = class_prefix_mobile+FIELD_DATETIME_CLASS


            self.msg_success_class = MSG_SUCCESS_CLASS 
            self.msg_failure_class = MSG_FAILURE_CLASS
            self.msg_process_dialog = current.T(MSG_PROCESS_DIALOG, lazy=False)
            self.process_dialog_class = PROCESS_DIALOG_CLASS
            self.vertical = vertical
            
            if oninit and callable(oninit):
                oninit(self)
            
        if hasattr(self, 'table') and self.table and \
                                                hasattr(self, 'define_header'):
            # key list
            key_fields = []
            if hasattr(self.table, '_primarykey'):
                for key in self.table._primarykey:
                    key_fields.append(key)
            else:
                key_fields = [self.table._id.name]
            header = Header(self.define_header(
                    header, key_fields, self.showid, self.editid), key_fields)

        if isinstance(header, Header):
            self.header = header
        else:
            self.header = Header(header)

        self.deletable = deletable
        self.formkey_id = FORMKEY_ID
        self.msg_error_id=MSG_ERROR_ID
        self.cell_error_class=CELL_ERROR_CLASS
        self.table_hash_available = TABLE_HASH_AVAILABLE
        self.record_hash_available = RECORD_HASH_AVAILABLE
        self.hash_salt_length = HASH_SALT_LENGTH 
        self.hash_salt = None
        self.hash_table = None
        self.editable = None
        self.validate_all = False 
        self.errors = None
        self.o_record = None
        self.next = None

    @staticmethod
    def init():
        def extract(func):
            r=func() 
            if request.ajax:
                if isinstance(r, dict):
                    for v in r.values():
                        if isinstance(v, EDITABLE):
                            return v
            return r
        
        from gluon import current
        response = current.response
        request = current.request
        response.files.append(URL('static/plugin_sqleditable/js',
                                                    'mindmup-editabletable.js'))
        response._caller=extract         

    def check_salt(self, salt, base64=False):
        if self.hash_salt_length <= 0:
            return ''
        if not salt:
            salt = urandom(self.hash_salt_length)
        elif len(salt) != self.hash_salt_length:
            try:
                salt = salt.decode('base64')
            except:
                salt = None
            finally:
                if salt and len(salt) != self.hash_salt_length:
                    salt = self.check_salt(None)
        if base64:
            return salt.encode('base64')
        else:
            return salt
        
    def generate_hash(self, text, use_salt=True):
        if use_salt is False:
            salt = ''
        elif self.hash_salt_length and not self.hash_salt:
            salt = self.hash_salt = self.check_salt(None)
        else:
            salt = self.hash_salt if self.hash_salt else ''
        return simple_hash(text, salt=salt, digest_alg=HASH_ALGORITHM)

    def compress_key_value(self, record):
        '''
        record: Record obj -> str ex keyvalue1|keyvalue2|keyvalue3
                str        -> list ex. [keyvalue1,keyvalue2,keyvalue3]
        '''
        if not record:
            return ''
        elif isinstance(record, Record):
            value = ''
            if record.has_field(NEWRECORD_FLAG_FIELD) is False:
                for _, v in record.key_value():
                    value = value + '|' + str(v) if value else str(v)
            return value
        else:
            return record.split('|')

    def generate_tablehash(self, formkey):
        if self.session:
            keys = []
            tablehashes = []
            if self.hash_table:
                tablehash = self.hash_table
            else:
                for rec in self.record:
                    keys.append(self.compress_key_value(rec))
                    if rec.has_field(RECORD_HASH_FIELD):
                        tablehashes.append(rec[RECORD_HASH_FIELD])
                keys.extend(tablehashes)
                serialized = '|'.join(str(k) for k in keys if k)
                tablehash = self.generate_hash(serialized)
            hash_salt = self.check_salt(self.hash_salt, base64=True)
            hashname =  TABLEHASH_STRING % self.formname
            self.session[hashname] = list(self.session.get(hashname,[]))[-4:] +\
                                        [[formkey, [tablehash, hash_salt]]]
            return tablehash
        else:
            return None 

    def generate_formkey(self):
        if self.session:
            formkey = web2py_uuid()
            keyname =  FORMKEY_STRING % self.formname
            self.session[keyname] = list(self.session.get(keyname,[]))[-4:] +\
                                                                    [formkey]
            return formkey
        else:
            return None 

    def set_formkey(self, formkey):
        hidden  = [INPUT(_type='hidden', _id=self.formkey_id, _value=formkey),
                   INPUT(_type='hidden', _id=self.formname_id, 
                                                        _value=self.formname)]
        return DIV((hidden), _style="display:none;")

    def check_tablehash(self, formkey, editable):
        # check editable object
        if not editable:
            return False
        elif not isinstance(editable, DIV):
            editable = TAG(editable)

        keys = []
        recordhashes = []
        tablehash = None
        r = 0
        cond = True
        while cond:
            el = self.pick_element(editable, r, special='key')
            if el:
                value = el[KEY_ID_TAG_ATTR]
                hash = el[RECORD_HASH_TAG_ATTR] 
                if value:
                    keys.append(value.decode('base64'))
                if hash:
                    recordhashes.append(hash)
            else:
                break
            r += 1
        keys.extend(recordhashes)
        serialized = '|'.join(str(k) for k in keys)

        if self.session:
            hashname =  TABLEHASH_STRING % self.formname
            tablehashes = dict(self.session.get(hashname, []))
            if(formkey and tablehashes and formkey in tablehashes):
                (tablehash,hash_salt) = tablehashes[formkey]
                self.hash_salt = self.check_salt(hash_salt)
                tablehashes.pop(formkey)
                self.session[hashname] = \
                                    [[k, tablehashes[k]] for k in tablehashes]
                tablehash_editable = self.generate_hash(serialized)
                if tablehash == tablehash_editable:
                    self.hash_table = tablehash
                    return True
                else:
                    return False
            else:
                return False
        else:
            return False
        
    def check_formkey(self, formkey):
        if self.session:
            keyname =  FORMKEY_STRING % self.formname
            formkeys = list(self.session.get(keyname, []))
            if(formkey and formkeys and formkey in formkeys):
                self.session[keyname].remove(formkey)
                return True
            else:
                return False
        else:
            return False

    def generate_inputhash(self, record):
        serialized = '|'.join(str(v) for _, v in record.writable() if v)
        return self.generate_hash(serialized, use_salt=False)

    def check_inputhash(self, record):
        if not record[INPUT_HASH_FIELD]:
            return True
        if self.generate_inputhash(record) == record[INPUT_HASH_FIELD]:
            return True
        return False
    
    def refresh_editable(self, editable):
        if self.next and not self.errors:
            script = 'location.href = "%s"' % self.next
            return DIV(SCRIPT(script, _type='text/javascript'), editable)
        
        if not isinstance(editable, DIV):
            editable = TAG(editable)
        # select
        selects = editable.elements('select')
        for select in selects:
            div = select.sibling('div')
            value = div[0] if len(div) > 0 else None
            if value:
                value = value.split(',')
                for option in select.components:
                    if option['_value'] in value:
                        option['_selected'] = True
                    else:
                        option['_selected'] = False
            elif not select['_multiple']:
                for option in select.components:
                    if option['_value'] == value:
                        option['_selected'] = True
                    else:
                        option['_selected'] = False
                
        # checkbox
        checkboxs = editable.elements(_type='checkbox')
        for checkbox in checkboxs:
            checkbox['_checked'] = True if checkbox['_value']=='on' else False
        # formkey
        formkey = self.generate_formkey()
        editable.element(_id=self.formkey_id).attributes['_value'] = formkey
        # tablehash
        if self.table_hash_available:
            self.generate_tablehash(formkey)
        # errors
        if self.errors:
            message = ''
            for error in self.errors:
                message = CAT(message, DIV(error, _id=self.msg_error_id, 
                                                        _class=MSG_ERROR_CLASS))
            editable = DIV(message, editable)
        return editable

    def build_editable_header(self):
        head = [TH(self.lineno_label)] if self.lineno else []
        if self.vertical:
            if self.deletable:
                head.append(TH(self.deleteable_label, _class=DELETABLE_CLASS))
                
            for f in self.header.readable():
                head.append(TH(f.label))
        else:
            if self.lineno:
                maxrow = self.maxrow if self.maxrow else len(self.record)
                line = [TH('%0d' % r) for r in range(1, maxrow+1)]
            else:
                return None
            head.extend(line)
        return THEAD(TR(head))

    def __field_tag(self, field, value, rowno, p_class, p_style, p_disabled):
        id = field.name
        type = field.type
        
        if field.has_attr('inset'):
            default = field.inset['zero'] if 'zero' in field.inset else ''
            multiple = field.inset['multiple'] if 'multiple' in field.inset \
                                                                    else False
            if not value:
                value = default                
            if isinstance(value, (list,tuple)):
                v = ','.join(value)
            else:
                v = value
            text = DIV(v, _style='display:none;',
                       _id=CELL_ID_FORMAT % dict(field=id, row=rowno))
            opt = [OPTION(SELECTBOX_DEFALUT_LABEL, _value='')] \
                                                        if not multiple else []
            if field.inset['labels']:
                opt += [OPTION(l, _value=v) for v, l in \
                        map(None, field.inset['theset'], field.inset['labels'])]
            else:
                opt += field.inset['theset']
                
            select = SELECT(
                    opt,
                    value= value, 
                    _disabled=p_disabled,
                    _multiple= multiple,
                    _style='width:100%;')
            value = [select, text]
            p_class.append(FIELD_SELECT_CLASS)
            p_class.append('parent')
            id_type = PARENT_ID_FORMAT
            
        elif type == 'boolean':
            value = INPUT(
                    _type='checkbox',
                    _checked=True if value else False,
                    _value = 'on' if value else 'off',
                    _disabled=p_disabled,
                    _id=CELL_ID_FORMAT % dict(field=id, row=rowno))
            p_class.append('parent')
            id_type = PARENT_ID_FORMAT

        elif type == 'date':
            p_class.append(self.field_date_class)
            id_type = CELL_ID_FORMAT
            
        elif type == 'time':
            p_class.append(self.field_time_class)
            id_type = CELL_ID_FORMAT
            
        elif type == 'datetime':
            p_class.append(self.field_datetime_class)
            id_type = CELL_ID_FORMAT
            
        else:
            id_type = CELL_ID_FORMAT

        p_class.append(FIELD_CLASS_PREFIX + str(id))
        p_class = ' '.join(p_class) if p_class else False
        p_style = ' '.join(p_style) if p_style else False
        td = TD(value, _style=p_style, _class =p_class,
                _disabled=p_disabled, _name=type,
                _id=id_type % dict(field=id, row=rowno))
        return td
    
    def __deletable_tag(self, rowno):
        value = INPUT(_type='checkbox', _checked=False, _value='off',
                      _id=DELETABLE_ID_FORMAT % dict(row=rowno))
        td = TD(value, _class=DELETABLE_CLASS + ' parent') 
        return td
        
    def __key_tag(self, record, rowno):
        parm = {}
        if rowno is not None:
            parm[KEY_ID_TAG_ATTR] = \
                            self.compress_key_value(record).encode('base64')
            id = KEY_ID_FORMAT % dict(row=rowno)
        else:
            id = False
        if record:
            if record.has_field(RECORD_HASH_FIELD): 
                parm[RECORD_HASH_TAG_ATTR] = record[RECORD_HASH_FIELD]
            if record.has_field(INPUT_HASH_FIELD): 
                parm[INPUT_HASH_TAG_ATTR] = record[INPUT_HASH_FIELD]
        td = TD(_class=NO_EDIT_CLASS, _id = id, _style="display:none;", **parm) 
        return td
        
    def build_editable_body(self):
                
        def newrecord():
            record = Record({}, self.header)
            record[NEWRECORD_FLAG_FIELD] = True
            for f in self.header.all():
                record[f.name] = f.default
            record[INPUT_HASH_FIELD] = self.generate_inputhash(record)
            return record
            
        def set_record(rowno):
            if rowno < len(self.record):
                return self.record[rowno]
            else:
                return new_record
        
        maxrow = self.maxrow if self.maxrow else len(self.record)
        contents = []

        for record in self.record:
            record[INPUT_HASH_FIELD ] = self.generate_inputhash(record)
        new_record = newrecord()

        if self.vertical:
            first = True
            for r in xrange(maxrow):
                record = set_record(r)
                line = [TH('%0d' % (r+1))] if self.lineno else []
                if self.deletable:
                    line.append(self.__deletable_tag(r))
                for f, v in record.all():
                    p_class = []
                    p_style = []
                    p_disabled = False

                    if not f.readable:
                        p_style.append("display:none;")
                    if not f.writable:
                        p_disabled = True
                        p_class.append(NO_EDIT_CLASS)
                    if first and f.readable and f.writable:
                        p_class.append(FIRST_CELL_CLASS)
                        first = False

                    value = v if not v is None else ''
                    line.append(self.__field_tag(f, value, r, p_class, p_style,
                                                                    p_disabled))
                line.append(self.__key_tag(record, r))
                contents.append(TR(line))
        else:
            if self.deletable:
                line = [TH(self.deleteable_label, _class=DELETABLE_CLASS)]
                for r in xrange(maxrow):
                    line.append(self.__deletable_tag(r))
                contents.append(TR(line))
                                
            first = True
            for f in self.header.all():  
                line = []
                if f.readable:
                    line.append(TH(f.label))
                     
                for r in xrange(maxrow):
                    record = set_record(r)
                    p_class = []
                    p_style = []
                    p_disabled = False

                    if not f.readable:
                        p_style.append("display:none;")
                    if not f.writable:
                        p_disabled = True
                        p_class.append(NO_EDIT_CLASS)
                    if first and f.readable and f.writable:
                        p_class.append(FIRST_CELL_CLASS)
                        first = False

                    value = record[f.name] if not record[f.name] is None else ''
                    line.append(self.__field_tag(f, value, r, p_class, p_style, 
                                                                    p_disabled))
                contents.append(TR(line))

            line = []
            line.append(self.__key_tag(None, None))     # title 
            for r in xrange(maxrow):
                record = set_record(r)
                line.append(self.__key_tag(record, r))
            contents.append(TR(line))

        return TBODY(contents)

    def process_dialog(self, message=''):
        if isinstance(message, (str, unicode)):  
            dialog = DIV(DIV(message, _class='modal-header'),
                         DIV(DIV(DIV(_class='bar', _style='width: 100%;'),
                                 _class='progress progress-striped active'),
                             _class='modal-body'),
                        _class='%s modal hide fade' % self.process_dialog_class)
        else:
            dialog = message
        return dialog

    def add_button(self, id, value, _class, _style):
        if isinstance(value, (str, unicode)):
            text = value
        elif value is None:
            text = AJAX_BUTTON_VALUE
        else:
            text = None
        if text:
            value = SPAN(I(_type='button', _class='icon-ok icon-white', 
                           _style='margin-right: 5px;'), text)

        return BUTTON(value, _type='button', _class=_class, _style=_style, 
                      _id=id)

    def build_js(self):
        """
        build javascript for field check and ajax.  
        """
        # js snipped
        onload  = "jQuery(document).ready(function () {%s});\n"
        bind    = "jQuery('#%s').on('load', function () {%s});\n"
        triger  = "jQuery('#%s').trigger('load');\n" % self.editable_id
        tb_js   = "jQuery('#%s').editableTableWidget();\n" % self.editable_id
        validate= "jQuery('#%s').on('validate', 'td.%s', function (evt, value) {%s});\n"
        if_js   = "if(!(%s)){return false;\n}"
        elif_js = "else if(!(%s)){return false;\n}"
        else_js = "else{return !!(%s);\n}"
        noif_js = "return !!(%s);\n"
        condition \
          = {'range'  :"value >= %d && value <= %d",
             'length' :"value.trim().length >= %d && value.trim().length <= %d",
             'integer':"value == parseInt(value) || value == ''",
             'number' :"(!isNaN(parseFloat(value)) && isFinite(value)) || value==''"}
        focus  = "jQuery('.%s').focus();" % FIRST_CELL_CLASS
             
        ajax    = \
"""
jQuery('#%(ajax_button_id)s').on('click', function () {
    jQuery.ajax({
        url: '%(url)s',
        type: 'POST',
        dataType: 'html',
        data: { %(editable_id)s: jQuery('#%(editable_id)s').html(),
            formkey: jQuery('#%(formkey_id)s').val(),
            formname: jQuery('#%(formname_id)s').val()
        },
        beforeSend: function (xhr) {
            jQuery('.%(process_dialog)s').modal({
                backdrop: 'static',
                keyboard: false
            });
        }
    })
    .done(function (data) {
        jQuery('#%(editable_id)s').html(data);
        if (document.getElementById('%(msg_error_id)s')) {
            jQuery('.%(msg_failure)s').show();
            jQuery('.%(msg_success)s').hide();
        } else {
            jQuery('.%(msg_success)s').show();
            jQuery('.%(msg_failure)s').hide();
        }
    })
    .fail(function (data) {
        jQuery('.%(msg_success)s').hide();
        jQuery('.%(msg_failure)s').show();
    })
    .always(function (data) {
        jQuery('.%(process_dialog)s').modal('hide');
        jQuery('.%(first_cell)s').focus();
    });
});
""" % dict( url=self.url, 
            editable_id=self.editable_id, 
            ajax_button_id=self.ajax_button_id, 
            formkey_id=self.formkey_id, 
            formname_id=self.formname_id, 
            msg_success=self.msg_success_class, 
            msg_failure=self.msg_failure_class,
            msg_error_id=self.msg_error_id, 
            process_dialog=self.process_dialog_class,
            first_cell = FIRST_CELL_CLASS)
        
        keydown_js =\
"""
jQuery(document).on('keydown', 'td:not(.%(noedit)s,.%(deletable)s)', function (e) {
    var child = jQuery(this).children(':checkbox, select');
    if (child.is(':checkbox')) {
        if ( e.which === 13) {
            child.trigger('click');
            return false;
        }
    } else if (child.is('select')) {
        if ( e.which === 13 ) {
            child.focus();
            return false;
        }
    }
});
jQuery(document).on('keydown', 'select', function (e) {
    if ( e.which === 13 || e.which === 9 || e.which === 27 ) {
        jQuery(this).parent('td').focus();
	return false;
    }
});
""" % dict(noedit=NO_EDIT_CLASS, deletable=DELETABLE_CLASS)
        
        checkbox_js =\
"""
jQuery(document).on('click', ':checkbox', function (e) {
    if (jQuery(this).prop('checked')) {
        jQuery(this).val('on');
    } else {
        jQuery(this).val('off');
    }
    e.stopPropagation();
});
jQuery(document).on('click', 'td:not(.%(noedit)s):has(:checkbox)', function(e){
    jQuery(this).children(':checkbox').trigger('click');
});
""" % dict(noedit=NO_EDIT_CLASS)  
            
        select_js =\
"""
jQuery(document).on('change', 'td:not(.%(noedit)s)>select', function () {
    jQuery(this).next('div').text(jQuery(this).val());
});
""" % dict(noedit=NO_EDIT_CLASS)  
     
        date_time_js = \
"""
jQuery(document).on('blur', 'input.%(field_class)s' , function (e) {
        var id = jQuery(this).attr('data-id');
        jQuery(this).hide();
        jQuery('#'+id).text(jQuery(this).val());
});
jQuery(document).on('keypress', 'input.%(field_class)s' , function (e) {
    if ( e.which === 13 ) {
        var id = jQuery(this).attr('data-id');
        jQuery(this).hide();
        jQuery('#'+id).text(jQuery(this).val()).focus();
        return false;
    }
});
"""

        # build logics
        script = tb_js
        # javascript validate
        if self.validate_js:
            for f in self.header.readable():
                cond = []
                if f.has_attr('range'):
                    cond.append(condition['range'] % tuple(f.range))
                if f.has_attr('length'):
                    cond.append(condition['length'] % tuple(f.length)) 
                if f.type == 'integer':
                    cond.append(condition['integer'])
                elif f.type == 'number':
                    cond.append(condition['number'])

                js = ''
                last = len(cond)-1
                for n, cd in enumerate(cond):
                    if n == 0 and last == 0:
                        js += noif_js % cd
                    elif n == 0:
                        js += if_js % cd
                    elif n > 0 and n < last:
                        js += elif_js % cd
                    else:
                        js += else_js % cd
                if js:
                    script += validate % (self.editable_id,
                                        FIELD_CLASS_PREFIX + str(f.name), js)
        # date/time/checkbox/listbox
        date = time = datetime= boolean = select = False
        for f in self.header.readable():
            if boolean is False and \
               ((f.type == 'boolean' and f.writable == True) or self.deletable):
                script += checkbox_js
                boolean = True
            if date is False and (f.type == 'date' and f.writable==True):
                script += date_time_js % dict(field_class=self.field_date_class)
                date = True
            if time is False and (f.type == 'time' and f.writable==True): 
                script += date_time_js % dict(field_class=self.field_time_class)
                time = True
            if datetime is False and \
                                    (f.type == 'datetime' and f.writable==True): 
                script += date_time_js % \
                                    dict(field_class=self.field_datetime_class)
                datetime = True
            if select is False and f.has_attr('inset'):
                script += select_js
                select = True

        script += keydown_js
        script = bind % (self.editable_id, script)
        script += triger
        script += focus
        script += ajax
        script = onload % script
        return script

    def build_editable(self):
        # editable
        head = self.build_editable_header()
        body = self.build_editable_body()
        contents = [head, body] if head else body
        editable = DIV(TABLE(contents, _class=self.table_class), 
                    _id=self.editable_id)
        # formkey/formname
        formkey = self.generate_formkey()
        div = self.set_formkey(formkey)
        e = editable.element(_id=self.editable_id)
        e[0] = CAT(e[0], div)
        # tablehash
        if self.table_hash_available:
            self.generate_tablehash(formkey)
        # button
        btn = self.add_button(self.ajax_button_id, self.ajax_button_value,
                               self.ajax_button_class, self.ajax_button_style)
        # js
        script = self.build_js()
        # process dialog
        dialog = self.process_dialog(self.msg_process_dialog)
        
        return [editable, btn, dialog, SCRIPT(script, _type='text/javascript')]

    def pick_element(self, editable, rowno, field=None, mode=None, 
                                                                special=None):
        '''
        pick the element of editable.
            editable : editable object
            rowno    : row number
            field    : field name
                       None: use special parameter
            mode     : None: pick the field tag.
                       'td': pick the parent td-tag (the case of nested).
                       'td-all': pick all field td-tags of record.
            special  : special fields. 
                       'key':key
                       'deletable':deletable flag 
        '''
        def field_element(field, mode=None):
            id = CELL_ID_FORMAT % dict(field=field, row=rowno)
            el = editable.element(_id=id)
            if mode=='td' and el.tag != 'td':
                    return el.parent
            return el
        def key_element():
            id = KEY_ID_FORMAT % dict(row=rowno)
            return editable.element(_id=id)
        def deletable_element(mode=None):
            id = DELETABLE_ID_FORMAT % dict(row=rowno)
            el = editable.element(_id=id)
            if mode == 'td':
                return el.parent
            return el
            
        if mode == 'td-all':
            td_tags = []
            td = deletable_element('td')
            if td:
                td_tags.append(td)
            for f in self.header.readable():
                td = field_element(f.name, mode='td')
                if td:
                    td_tags.append(td)
            return td_tags
        else:
            if special == 'key':
                return key_element()
            elif special == 'deletable':
                return deletable_element()
            else:
                return field_element(field, mode=mode)
                
    def update_field_element(self, editable, rowno, value, field=None, 
                                                                special=None):
        # key value & recordhash
        if special == 'key':
            if isinstance(value, dict):
                el = self.pick_element(editable, rowno, special='key')
                if el:
                    if 'key_value' in value:
                        el[KEY_ID_TAG_ATTR] = value['key_value']
                    if 'record_hash' in value:
                        el[RECORD_HASH_TAG_ATTR] = value['record_hash']
                    if 'input_hash' in value:
                        el[INPUT_HASH_TAG_ATTR] = value['input_hash']
        # field
        elif field:
            el = self.pick_element(editable, rowno, field)
            if hasattr(el,'tag') and el.tag=='input/' and \
                                                    el['_type']=='checkbox':
                el['_value'] = 'on' if value else 'off'
            elif len(el) > 0:
                el[0] = value
            elif hasattr(el,'tag') and el.tag=='td':
                td = TD(value, _class=el['_class'], _id=el['_id'], 
                                _name=el['_name'], _tabindex=el['_tabindex'],
                                _style=el['_style'])
                editable.element(_id=el['_id'], replace=td)
    
    def set_error_class(self, editable, rowno, field=None):
        if field:
            el = self.pick_element(editable, rowno, field, mode='td')
            el.add_class(self.cell_error_class)
        else:
            els = self.pick_element(editable, rowno, field, mode='td-all')
            for el in els:
                el.add_class(self.cell_error_class)

    def readout_editable(self, editable, table=None):
        '''
        readout editable & check error (if table exsit) 
        '''
        def readout_element(rowno, f=None, special=None):
            if special == 'key':
                el = self.pick_element(editable, rowno, special='key')
                if el is None:
                    return None, None
                value = self.compress_key_value(
                                        el[KEY_ID_TAG_ATTR].decode('base64'))
                recordhash = el[RECORD_HASH_TAG_ATTR]
                inputhash = el[INPUT_HASH_TAG_ATTR]
                return (value, recordhash, inputhash), el
            elif special == 'deletable':
                el = self.pick_element(editable, rowno, special='deletable')
                if el is None:
                    return None, None
                value = value = True if el['_value']=='on' else False
            else:
                el = self.pick_element(editable, rowno, f.name)
                if el is None:
                    return None, None
                if hasattr(el,'tag') and el.tag=='input/' and \
                                                    el['_type']=='checkbox':
                    value = True if el['_value']=='on' else False
                elif len(el):
                    value = el[0]
                else:
                    value = ''
            return value, el

        def readout_record(rowno):
            record = Record({}, self.header)
            dummy_record = False
            # key
            value,el = readout_element(rowno, special='key')
            if el is None:
                return None
            elif value: 
                if value[0]:
                    keys = zip(self.header.key(),value[0])
                    for k,v in keys:
                        record[k.name] = v
                    record[STORED_KEY_VALUE] = \
                                            dict([(k.name, v) for k, v in keys])
                if value[1]:
                    record[RECORD_HASH_FIELD] = value[1]
                    if value[1] == DUMMY_RECORD_HASH_VALUE:
                        dummy_record = True
                if value[2]:
                    record[INPUT_HASH_FIELD] = value[2]
            if not value or (value and not value[0]):
                record[NEWRECORD_FLAG_FIELD] = True
            # delete flag
            if self.deletable and dummy_record is False:
                value,el = readout_element(rowno, special='deletable')
                if el is None:
                    return None
                if value is True:
                    record[DELETE_FLAG_FIELD] = True
            # fields
            for f in self.header.writable():
                value,el = readout_element(rowno, f)
                if el is None:
                    return None
                if f.has_attr('inset.multiple') and f.inset['multiple'] and \
                                                                ',' in value:
                    record[f.name] = value.split(',')
                else:
                    record[f.name] = value
            return record

        # check editable object
        if not editable:
            return False
        elif not isinstance(editable, DIV):
            editable = TAG(editable)
            
        # remove error message & error class
        editable.elements(_id=self.msg_error_id, replace=None)
        els = editable.elements('td.%s' % self.cell_error_class)
        for el in els:
            el.remove_class(self.cell_error_class)

        records = RecordArray([], self.header)
        r = 0
        cond = True
        while cond:
            record = readout_record(r)
            if record is None:
                cond = False
                break
            if self.check_inputhash(record):
                if not record.has_field(DELETE_FLAG_FIELD):
                    record[NOTCHANGED_FLAG_FIELD] = True
            elif table and self.validate_all is True:
                self.record_validate(record, r, editable)
            records.append(record)
            r += 1
        return records, editable

    def as_dict(self):
        if self.editable:
            self.editable = self.refresh_editable(self.editable)
            return self.editable
        else:
            editable = self.build_editable()
            return {'editable':DIV(editable[0],editable[2]),
                    'button': editable[1], 'script': editable[3]}

    def xml(self):
        if self.editable:
            self.editable = self.refresh_editable(self.editable)
            return self.editable
        else:
            return DIV(self.build_editable()).xml()

    def is_ajax(self):
        from gluon import current
        request_vars = current.request.post_vars
        if  request_vars and hasattr(request_vars, self.editable_id):
            return True
        else:
            return False
    
    def is_touch_device(self):
        from gluon import current
        user_agent = current.request.user_agent()
        if user_agent.is_mobile or user_agent.is_tablet:
            return True
        else:
            return False
    
    def set_language(self):
        from gluon import current
        request_vars = current.request.env
        if request_vars.http_accept_language:
            return request_vars.http_accept_language[:2]
        else:
            'en'

    def process(self, **kwargs):  
        self.next = kwargs.get('next', None)
        if 'next' in kwargs:
            del kwargs['next']
        FORM.process(self, **kwargs)
        return self

    def accepts(self, request_vars, session=None, formname=FORMNAME, 
                onvalidation=None, hideerror=False, **kwargs):
                    
        if request_vars.__class__.__name__ == 'Request':
            request_vars = request_vars.post_vars
        self.request_vars = Storage()
        self.request_vars.update(request_vars)
        self.session = session
        self.formname = formname
        if not self.next:
            self.next = kwargs.get('next', None)
        self.errors = []

        status = True
        if not request_vars:
            status = False
        elif formname != request_vars.formname:
            status = False
        elif not self.check_formkey(request_vars.formkey):
            status = False
        elif self.table_hash_available and \
            not self.check_tablehash(request_vars.formkey, 
                                     request_vars[self.editable_id]):
            status = False
        if status and request_vars[self.editable_id]:
            table = {'table':self.table} if hasattr(self, 'table') else {}
            self.o_record,self.editable = \
                self.readout_editable(request_vars[self.editable_id], **table)
            if self.errors:
                status = False
        else:
            status = False
        self.accepted = status
        return status
        
class SQLEDITABLE(EDITABLE):
    def __init__(self, table, record=None, deletable=False, header=None,
                 maxrow=None, lineno=True,  url=None, showid=True, editid=False,
                 validate_js=True, vertical=True, oninit=None, **kwargs):
                 
        self.table = table
        self.showid = showid
        self.editid = editid

        EDITABLE.__init__(self, record, header, maxrow, lineno, url, 
                          validate_js, vertical, deletable, oninit, **kwargs)

        # record list
        if self.is_ajax() is False:
            if self.record and not isinstance(self.record, RecordArray):
                self.record = self.db_read(self.record)
            elif self.record is None:
                self.record = self.db_read(record)
                
    def define_header(self, fields=None, key_fields=None ,showid=True, 
                                                                editid=False):
        '''
        define header list
        - table: Table object
        - fields: list of fields for header
        '''
        def check_validators(requires):
            h = {}
            if not isinstance(requires, (list, tuple)):
                requires = [requires]
            for validator in requires:
                s = str(validator)
                if 'IS_DECIMAL_IN_RANGE' in s or \
                    'IS_FLOAT_IN_RANGE' in s or \
                     'IS_INT_IN_RANGE' in s:
                    h['range'] = [validator.minimum, validator.maximum]
                elif 'IS_LENGTH' in s:
                    h['length'] = [validator.minsize, validator.maxsize]
                elif 'IS_IN_SET' in s:
                    h['inset'] = {'multiple': validator.multiple,
                                    'zero': validator.zero,
                                    'theset': validator.theset,
                                    'labels': validator.labels}
            return h
        
        table = self.table
        
        if fields is None:
            fields = table.fields
        header = []

        for f in fields:
            if isinstance(f, dict):
                header.append(f)
            else:
                if table[f].readable:
                    h = {'field': f}
                    h.update(check_validators(table[f].requires))
                    if table[f].type == 'integer' or table[f].type == 'bigint' :
                        h['type'] = 'integer'
                    elif table[f].type == 'double':
                        h['type'] = 'number'
                    elif table[f].type == 'float':
                        h['type'] = 'number'
                    elif table[f].type.startswith('decimal'):
                        _,scale = table[f].type[7:].strip('()').split(',')
                        if scale ==0 :
                            h['type'] = 'integer'
                        else:
                            h['type'] = 'number'
                    elif table[f].type == 'boolean':
                        h['type'] = 'boolean'        
                    elif table[f].type == 'datetime':
                        h['type'] = 'datetime'        
                    elif table[f].type == 'date':
                        h['type'] = 'date'        
                    elif table[f].type == 'time':
                        h['type'] = 'time'        
                    else:
                        h['type'] = 'string'
                    
                    if self.table[f].name in key_fields:
                        h['writable'] = table[f].writable if editid else False
                        h['readable'] = table[f].readable if showid else False 
                    else:
                        h['writable'] = table[f].writable
                        h['readable'] = table[f].readable
                    if table[f].default is None:
                        if 'inset' in h:
                            if 'zero' in h['inset'] and h['inset']['zero']:
                                h['default'] = h['inset']['zero']
                        elif h['type'] == 'boolean':
                            h['default'] = False
                        else:
                            h['default'] = ''
                    else:
                        h['default'] = table[f].default
                    h['label'] = table[f].label
                    header.append(h)
        return header

    def field_validate(self, requires, value):
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        for validator in requires:
            try:
                value,error = validator(value)
            except NotImplementedError:
                pass
            except:
                error = 'unknown error'
            if error:
                return value, error
        return value, None

    def record_validate(self, record, rowno, editable=None):
        if editable is None:
            editable = self.editable
        status = True
        for f,v in record.writable():
            if isinstance(self.table[f.name], Field):
                value,error = \
                        self.field_validate(self.table[f.name].requires, v)
                # set error class
                if error:
                    self.set_error_class(editable, rowno, f.name)
                    if not error in self.errors:
                        self.errors.append(error)
                    status = False
                else:
                    record[f.name] = value
        return status

    def generate_recordhash(self, record):
        serialized = '|'.join(str(v) for _, v in record.all() if v)
        return self.generate_hash(serialized)

    def table_set(self, record):
        cond = ''
        for k, v in record.key_value():
            cond = cond &(self.table[k.name] == v) if cond else \
                                                        self.table[k.name] == v
        return self.table._db(cond)
        
    def table_row_as_dict(self, record):
        row = self.table_set(record).select().first()
        if row:
            return Record(row.as_dict(), self.header)
        else:
            return None
            
    def set_recordhash_error(self, rowno, changed=True):
        self.set_error_class(self.editable, rowno)
        from gluon import current
        if changed:
            error = current.T(MSG_RECORD_HASH_CHANGED)
        else:
            error = current.T(MSG_RECORD_HASH_DELETED)
        if not error in self.errors:
            self.errors.append(error)

    def check_recordhash(self, record=None, target='record'):
        '''
        record : check record (when target='record')
        target
            'record'    : check for the record
            'table'     : check for the table (all records)
        
        return value: True: matched recordhash
                      False: no matched recordhash
                      'notexit': record is not exsit 
                      'dummy': dummy record
        '''
        def compare_recordhash(record):
            if record.has_field(RECORD_HASH_FIELD) is False:
                return False
            if record[RECORD_HASH_FIELD] == DUMMY_RECORD_HASH_VALUE:
                return 'dummy' 

            db_record = self.table_row_as_dict(record)
            if db_record is None:
                return 'notexit'
            recordhash = self.generate_recordhash(db_record)
            return recordhash == record[RECORD_HASH_FIELD]

        if target == 'record':
            if record.has_field(NEWRECORD_FLAG_FIELD):
                return True
            else:
                return compare_recordhash(record)
        elif target == 'table' and self.o_record:
            for r, rec in enumerate(self.o_record):
                if rec.has_field(NEWRECORD_FLAG_FIELD) is False:
                    recordhash_status = self.compare_recordhash(rec)
                    if recordhash_status in (False, 'notexit'):
                        changed = False if recordhash_status == 'notexit' else\
                                                                        True
                        self.set_recordhash_error(r, changed=changed)
                        return False
            return True
        return False
    
    def db_read(self, record=None):
        def format_record_data(record_data):
            fields = []
            for f in self.header.writable():
                if f.has_attr('inset.multiple') and f.inset['multiple']:
                    fields.append(f.name)
            if not fields:
                return record_data

            from gluon.dal import bar_decode_string
            for record in record_data:
                for field in fields:
                    if '|' in record[field]:
                        record[field] = bar_decode_string(record[field])
            return record_data

        if not record:
            limit = (0, self.maxrow) if self.maxrow else None
            record_data = self.table._db(self.table).select(limitby=limit)\
                                                                    .as_list()
            record_data = RecordArray(record_data, self.header)
            if self.record_hash_available:
                for rec in record_data:
                    rec[RECORD_HASH_FIELD] = self.generate_recordhash(rec)
            return format_record_data(record_data)
        else:
            record_data = RecordArray([], self.header)
            if isinstance(record, (list,tuple)):
                # repeated
                new_record = []
                for r in record:
                    if not r in new_record:
                        new_record.append(r)
                record = new_record
            elif isinstance(record, (int,long,str)):
                record = [record]
            else:
                RuntimeError('Invalid record parameter')

            for r in record:
                if not isinstance(r, (list,tuple)):
                    r = [r]
                rec = Record(dict([(k.name, f) for k, f in \
                                    zip(self.header.key(), r)]), self.header)
                rec = self.table_row_as_dict(rec)
                if rec:
                    if self.record_hash_available:
                        rec[RECORD_HASH_FIELD] = self.generate_recordhash(rec)
                    record_data.append(rec)
            return format_record_data(record_data)
    
    def db_cud(self):

        def db_create(record, rowno):
            fields = dict([(f.name,v) for f,v in record.writable()])
            try:
                result = self.table.insert(**fields)
            except Exception as e:
                error = str(e.message)
                result = False
            else:
                error = ''
            if not result:
                self.errors.append('[db insert error] ' + error)
                self.set_error_class(self.editable, rowno)
                return result
            else:
                if isinstance(result, dict):
                    for key in record.key_list():
                        record[key] = result[key]
                else:
                    key = record.key_list()[0]
                    record[key] = result
            
            rec = self.table_row_as_dict(record)
            if rec:
                value = {}
                value['key_value'] = \
                                self.compress_key_value(rec).encode('base64')
                if self.record_hash_available:
                    recordhash = self.generate_recordhash(rec)
                    value['record_hash'] = recordhash
                    record[RECORD_HASH_FIELD] = recordhash
                value['input_hash'] = self.generate_inputhash(rec)
                self.update_field_element(self.editable, rowno, value, 
                                                                special='key')
                del record[NEWRECORD_FLAG_FIELD]

                for key in record.key_list():
                    self.update_field_element(self.editable, rowno, 
                                                                rec[key], key)
            return result

        def db_update(record, rowno):
            fields = {}
            for f,v in record.writable():
                fields[f.name] = v
            if fields:
                try:
                    result = self.table_set(record).update(**fields)
                except Exception as e:
                    error = str(e.message)
                    result = False
                else:
                    error = ''
                if not result:
                    self.errors.append('[db update error] ' + error)
                    return result

                del record[STORED_KEY_VALUE]
                rec = self.table_row_as_dict(record)
                if rec:
                    value = {}
                    value['key_value'] = \
                                self.compress_key_value(rec).encode('base64')
                    if self.record_hash_available:
                        recordhash = self.generate_recordhash(rec)
                        value['record_hash'] = recordhash
                        record[RECORD_HASH_FIELD] = recordhash
                    value['input_hash'] = self.generate_inputhash(rec)
                    self.update_field_element(self.editable, rowno, value, 
                                                            special='key')
                return result
            else:
                return False

        def db_delete(record, rowno):
            result = True
            if record.has_field(NEWRECORD_FLAG_FIELD) is False:
                try:
                    result = self.table_set(record).delete()
                except Exception as e:
                    error = str(e.message)
                    result = False
                else:
                    error = ''
                if not result:
                    self.errors.append('[db delete error] ' + error)
                    return result

            els = self.pick_element(self.editable, rowno, mode='td-all')
            for el in els:
                el.add_class(NO_EDIT_CLASS)
                for child in ['input', 'select']:
                    child_el = el.element(child)
                    if child_el:
                        child_el['_disabled'] = 'disabled' 

            if self.record_hash_available:
                value = {'record_hash':DUMMY_RECORD_HASH_VALUE, 'input_hash':''}
                record[RECORD_HASH_FIELD] = DUMMY_RECORD_HASH_VALUE
                self.update_field_element(self.editable, rowno, value, 
                                                                special='key')
            return result

        # check recordhash for not parcel_update and not record_hash_available 
        recordhash_status = False
        if self.record_hash_available:
            if self.parcel_update is False:
                if self.check_recordhash(target='table') is False:
                    return False
                recordhash_status = True
        else:
            recordhash_status = True
        
        #create/update/delete
        status = True
        record_cud = False
        for r, rec in enumerate(self.o_record):
            if rec.has_field(NOTCHANGED_FLAG_FIELD):
                continue
            if rec.has_field(RECORD_HASH_FIELD) and \
                        rec[RECORD_HASH_FIELD] == DUMMY_RECORD_HASH_VALUE:
                continue
            if status is False:
                break
            if self.record_hash_available:
                if self.parcel_update:
                    recordhash_status = self.check_recordhash(rec)
                    if recordhash_status is False:
                        self.set_recordhash_error(r, changed=True)
                    elif recordhash_status == 'notexit':
                        self.set_recordhash_error(r, changed=False)

            if recordhash_status is True:
                if rec.has_field(DELETE_FLAG_FIELD):
                    status = db_delete(rec, r)
                    record_cud = True
                else:
                    if self.validate_all or self.record_validate(rec, r):
                        if rec.has_field(NEWRECORD_FLAG_FIELD):
                            status = db_create(rec, r)
                        else:
                            status = db_update(rec, r)
                        record_cud = True
            else:
                    status = False
        if status and record_cud:
            self.table._db.commit()
        return bool(status)
        
    def accepts(self, request_vars,session=None, formname='tb_%(tablename)s', 
                parcel_update=True, onvalidation=None, hideerror=False,
                **kwargs):
        if request_vars.__class__.__name__ == 'Request':
            request_vars = request_vars.post_vars
               
        self.parcel_update = parcel_update
        formname = formname % dict(tablename=self.table._tablename)
        status = EDITABLE.accepts(self, request_vars, session, formname,
                                                                    **kwargs)
        if status:
            status = self.db_cud()
            if status:
                self.record = self.o_record
                self.hash_table = None
        if self.errors:
            status = False
        self.accepted = status
        return status
    
        
