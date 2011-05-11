import copy

import django.template as template
import django.template.defaulttags as defaulttags

import templatetags
import request_handler

class TwoStageVariableDoesNotExist(Exception):
    pass

def raw_template_text_parse(parser, token):
    tag_mapping = {
        template.TOKEN_TEXT: ('', ''),
        template.TOKEN_VAR: ('{{', '}}'),
        template.TOKEN_BLOCK: ('{%', '%}'),
        template.TOKEN_COMMENT: ('{#', '#}'),
    }

    list_raw_tokens = [token]

    if token.token_type == template.TOKEN_BLOCK:
        tokens_orig = copy.deepcopy(parser.tokens)

        token_name = list(token.split_contents())[0]
        end_token_name = 'end' + token_name
        end_stack = [end_token_name]

        while parser.tokens:
            token_next = parser.next_token()

            if not token_next:
                raise Exception("Missing end of block token for raw template text parser")

            list_raw_tokens.append(token_next)

            if token_next.token_type == template.TOKEN_BLOCK:
                if token_next.contents == end_token_name:
                    end_stack.pop()
                    if len(end_stack) <= 0:
                        break
                else:
                    token_next_name = list(token_next.split_contents())[0]
                    if token_next_name == token_name:
                        end_stack.append(end_token_name)

        parser.tokens = tokens_orig

    list_raw_text = []
    for raw_token in list_raw_tokens:
        start, end = tag_mapping[raw_token.token_type]
        list_raw_text.append('%s%s%s' % (start, raw_token.contents, end))

    return "".join(list_raw_text)

resolve_var_old = template.resolve_variable
def resolve_var_new(path, context):
    try:
        return resolve_var_old(path, context)
    except template.VariableDoesNotExist:
        raise TwoStageVariableDoesNotExist

def get_new_render(old_render):
    def new_render(*args, **kw_args):
        try:
            return old_render(*args, **kw_args)
        except TwoStageVariableDoesNotExist:
            if hasattr(args[0], "raw_template_text"):
                return args[0].raw_template_text
            else:
                return "sneaky sneaky"
    return new_render

def get_new_parse(old_parse):
    def new_parse(parser, token):
        raw_template_text = raw_template_text_parse(parser, token)
        node = old_parse(parser, token)
        if node:
            node.raw_template_text = raw_template_text
        return node
    return new_parse

class TwoStageTest(request_handler.RequestHandler):

    #@two_stage_test
    def get(self):
        template.resolve_variable = resolve_var_new

        subclasses = template.Node.__subclasses__()
        for subclass in subclasses:
            if not hasattr(subclass, "monkeyed"):
                subclass.monkeyed = True
                subclass.render = get_new_render(subclass.render)

        for key in templatetags.register.tags.keys():
            old_parse = templatetags.register.tags[key]
            templatetags.register.tags[key] = get_new_parse(old_parse)

        for key in defaulttags.register.tags.keys():
            old_parse = defaulttags.register.tags[key]
            defaulttags.register.tags[key] = get_new_parse(old_parse)

        self.render_template("two_stage_template/two_stage_test.html", {"sheep": 1, "monkey": "ooh ooh aah aah"})


