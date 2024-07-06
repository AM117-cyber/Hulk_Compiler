from code_gen.visitor_code_generator import VisitorCodeGenerator

class CodeGenerator:
    def __call__(self, ast, context):
        declarations, main = self.generate(ast, context)
        with open('code_gen/c_utils.c') as c_utils:
            return c_utils.read() + "\n\n"

    @staticmethod
    def generate(ast, context):

        visitor = VisitorCodeGenerator()
        
        # -----------------DECLARATIONS-----------------
        declarations = ''
        types_dec = {}
        functions_dec = {}
        type_methods_dec = {}

        # Creando las declaraciones de los tipos como funciones que reciben
        # los parametros y atributos del tipo
        for type_ in context.types.values(): # No esta definido types en Context
            if type_.name not in ['String', 'Boolean', 'Object', 'Number']:
                type_dec = 'Object createType_' + type_.name + " ("

                # Declaraciones de los paramatros del tipo
                type_params = {}
                indexParam = 0 
                for param in type_.params_names:
                    type_dec += 'Object ' + param + '_param' + str(indexParam) + ', '
                    type_params[type_.name + '_param' + str(indexParam)] = param
                    indexParam += 1
                if indexParam > 0:
                    type_dec = type_dec[:-2]

                # Declaraciones de los atributos del tipo
                type_atts = {}
                indexAtt = 0 
                for att in type_.attributes:
                    type_dec += 'Object ' + att.name + '_att' + str(indexAtt) + ', '
                    type_atts[type_.name + '_att' + str(indexAtt)] = att.name
                    indexAtt += 1
                if indexAtt > 0:
                    type_dec = type_dec[:-2]

                type_dec += ')'

                types_dec[type_] = (type_dec, type_params, type_atts)

                declarations += type_dec + ';\n' 

                # Declaraciones de los metodos del tipo
                for method in type_.methods:
                    method_dec = 'Object method_' + type_.name + '_' + method.name + '('
                    indexMethodType = 0
                    for param in method.param_names:
                        method_dec += 'Object param_' + str(indexMethodType) + ', '
                        method.node.scope.children[0].find_variable(param).setNameC(type_.name + method.name + str(indexMethodType))
                        indexMethodType += 1
                    if indexMethodType > 0:
                        method_dec = method[:-2]
                    method_dec += ')'

                    type_methods_dec[method.name] = (method_dec, method)

        # Creando las declaraciones de las funciones globales
        for function in context.functions.values():
            function_dec = 'Object globalFunction_' + function.name + " ("

            # Declaraciones de los paramatros del tipo
            function_params = {}
            indexParam = 0 
            for param in function.param_names:
                function_dec += 'Object ' + param + '_param' + str(indexParam) + ', '
                function_params[function.name + '_param' + str(indexParam)] = param
                function.node.scope.children[0].find_variable(param).setNameC(function.name + str(indexParam))
                indexParam += 1
            if indexParam > 0:
                function_dec = function_dec[:-2]

            function_dec += ')'

            functions_dec[function] = (function_dec, function_params)

            declarations += function_dec + ';\n' 

        # -----------------DEFINITIONS-----------------
        definitions = ''
        types_def = {}
        functions_def = {}

        # Creando las definiciones de los tipos
        for type_ in types_dec.values():
            type_def = types_dec[type_][0] + '{\n'
            type_def += '\t' + 'Object obj = createObject();\n'

            # Añadiendo el nombre del tipo
            type_def += '\t' + 'addItem(obj, \"name\", \"'+ type_.name + '\");\n'
            # Añadiendo los parámetros del tipo
            for id_param, param in types_dec[type_][1]:
                type_def += '\t' + 'addItem(obj, \"' + id_param + '\", \"'+ param + '\");\n'
            # Añadiendo los atributos del tipo
            for id_att, att in types_dec[type_][2]:
                type_def += '\t' + 'addItem(obj, \"' + id_att + '\", \"'+ att + '\");\n'
            # Añadiendo los metodos del tipo
            indexMethod = 0
            for met in type_.methods:
                type_def += '\t' + 'addItem(obj, \"' + type_.name + '_method' + str(indexMethod) + '\", \"'+ met.name + '\");\n'
                indexMethod += 1
            # Añadiendo los protocolos del tipo
            indexProt = 0
            for prot in type_.protocols.values():
                type_def += '\t' + 'addItem(obj, \"' + type_.name + '_protocol' + str(indexProt) + '\", \"'+ prot + '\");\n'
                indexProt += 1
            # Añadiendo los ancestros del tipo
            indexParent = 0
            if type_.parent != None:
                type_def += '\t' + 'addItem(obj, \"parent' + str(indexParent) + '\", \"'+ type_.parent + '\");\n'
                indexParent = 1
            type_def += '\t' + 'addItem(obj, \"parent' + str(indexParent) + '\", \"Object\");\n'

            type_def += '}\n'
            types_def[type_.name] = type_def
            definitions += type_def + '\n'

        # Creando las definiciones de las funciones globales
        for function in functions_dec.values():
            function_def = functions_dec[function][0] + '{\n'
            function_def += '\t' + visitor.visit(function.node)