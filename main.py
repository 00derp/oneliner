import ast
import sys


## TODO: Detect which features are ACTUALLY needed, and modify the code accordingly.

## Need __print if we print
## Need __y if we use while
## Need __builtin__ if we use __print


## Typesetting abstractions


DUNDER_PRINT = "__print"
DUNDER_Y = "__y"

COMMA = ", "
CONTINUATION = "%s"

def lambda_function(arguments_to_values, prettyprinted=False):
    ## arguments_to_values :: {argument_i: value_i}
    ## :: string
    if prettyprinted:
        raise NotImplementedError
    else:
        return "(lambda " + (COMMA.join(arguments_to_values.keys())) + ": " + CONTINUATION + ")(" + (COMMA.join(arguments_to_values.values())) + ")"


### Actual logicky code begins here


def get_init_code(tree):
    ## Return a string with %s somewhere in.
    ## INIT_CODE = "(lambda __builtin__: (lambda __print, __y, __d: %s)(__builtin__.__dict__['print'],(lambda f: (lambda x: x(x))(lambda y: f(lambda *args: y(y)(*args)))),type('StateDict',(),__builtin__.__dict__)()))(__import__('__builtin__'))"

    ## TODO: Short-circuit to something far simpler if the program has but one print statement.
    need_print = True ## true if prints anywhere. TODO.
    need_y_combinator = True ## true if uses a while. TODO.
    # need_state_dict = True ## true if uses anything involving __d -- while, for, if. Also governs the list comprehension trick. TODO.
    need_dunderbuiltin = need_print or need_state_dict

    output = "%s"
    if need_dunderbuiltin:
        output = output % lambda_function({"__builtin__": "__import__('__builtin__')"})

    arguments = {}
    if need_print:
        arguments[DUNDER_PRINT] = "__builtin__.__dict__['print']"
    if need_y_combinator:
        arguments[DUNDER_Y] = "(lambda f: (lambda x: x(x))(lambda y: f(lambda *args: y(y)(*args))))"
    # if need_state_dict:
    #     arguments[DUNDER_D] = "type('StateDict',(),__builtin__.__dict__)()"

    if len(arguments.keys()) > 0:
        output = output % lambda_function(arguments)

    return output


## Parsing begins here

def fields(tree):
    return dict(list(ast.iter_fields(tree)))

def child_nodes(tree):
    return list(ast.iter_child_nodes(tree))

def many_to_one(trees, after='None'):
    # trees :: [Tree]
    # return :: string
    assert type(trees) is list
    if len(trees) is 0:
        return after
    else:
        return code_with_after(trees[0], many_to_one(trees[1:], after=after))

def code(tree):
    return code_with_after(tree, 'None')


def assignment_component(after, targets, value):
    return "(lambda %s: %s)(%s)" % (targets, after, value)
    ## return '[%s for %s in [(%s)]][0]' % (after, targets, value)


def code_with_after(tree, after):
    if type(tree) is ast.Add:
        return '+'
    elif type(tree) is ast.And:
        return ' and '
    elif type(tree) is ast.Assert:
        raise NotImplementedError("'assert' is an open problem.")
    elif type(tree) is ast.Assign:
        targets = [code(target) for target in tree.targets]
        value = code(tree.value)
        targets = ','.join(targets)
        return assignment_component(after, targets, value)
    elif type(tree) is ast.Attribute:
        return '%s.%s' % (code(tree.value), tree.attr)
    elif type(tree) is ast.AugAssign:
        target = code(tree.target)
        op = code(tree.op)
        value = code(tree.value)
        value = "%s%s%s" % (target, op, value)
        return assignment_component(after, target, value)
    elif type(tree) is ast.BinOp:
        return '(%s%s%s)' % (code(tree.left), code(tree.op), code(tree.right))
    elif type(tree) is ast.BitAnd:
        return '&'
    elif type(tree) is ast.BitOr:
        return '|'
    elif type(tree) is ast.BitXor:
        return '^'
    elif type(tree) is ast.BoolOp:
        return '(%s)' % code(tree.op).join([code(val) for val in tree.values])
    elif type(tree) is ast.Break:
        raise NotImplementedError("'break' is an open problem.")
    elif type(tree) is ast.Call:
        func = code(tree.func)
        args = [code(arg) for arg in tree.args]
        keywords = [code(kw) for kw in tree.keywords]
        if tree.starargs is None:
            starargs = []
        else:
            starargs = ["*"+code(tree.starargs)]
        if tree.kwargs is None:
            kwargs = []
        else:
            kwargs = ["**"+code(tree.kwargs)]
        elems = args + keywords + starargs + kwargs
        comma_sep_elems = ','.join(elems)
        return '%s(%s)' % (func, comma_sep_elems)
    elif type(tree) is ast.ClassDef:
        raise NotImplementedError("class definitions are not implemented.")
        ## Note to self: delattr and setattr are useful things
        ## also you're DEFINITELY going to want this:
        ## https://docs.python.org/2/library/functions.html#type
    elif type(tree) is ast.Compare:
        assert len(tree.ops) == len(tree.comparators)
        return code(tree.left) + ''.join([code(tree.ops[i])+code(tree.comparators[i]) for i in range(len(tree.ops))])
    elif type(tree) is ast.comprehension:
        return ('for %s in %s' % (code(tree.target), code(tree.iter))) + ''.join([' if '+code(i) for i in tree.ifs])
    elif type(tree) is ast.Continue:
        raise NotImplementedError("'continue' is an open problem.")
    elif type(tree) is ast.Delete:
        raise NotImplementedError("'delete' is not implemented.")
        ## Note also: globals() and locals() are useful here
        ## You can pop() from globals and/or locals to implement this
    elif type(tree) is ast.Dict:
        return '{%s}' % ','.join([('%s:%s'%(code(k), code(v))) for (k,v) in zip(tree.keys, tree.values)])
    elif type(tree) is ast.DictComp:
        return '{%s}' % (' '.join([code(tree.key)+":"+code(tree.value)] + [code(gen) for gen in tree.generators]))
    elif type(tree) is ast.Div:
        return '/'
    elif type(tree) is ast.Ellipsis:
        return '...'
    elif type(tree) is ast.Eq:
        return '=='
    elif type(tree) is ast.ExceptHandler:
        raise NotImplementedError("'except' is an open problem.")
    elif type(tree) is ast.Exec:
        raise NotImplementedError("'exec' is an open problem.")
    elif type(tree) is ast.Expr:
        code_to_exec = code(tree.value)
        return '(lambda ___: %s)(%s)' % (after, code_to_exec) ## TODO: ensure ___ isn't taken
    elif type(tree) is ast.Expression:
        return code(tree.body)
    elif type(tree) is ast.ExtSlice:
        return ', '.join([code(dim) for dim in tree.dims])
    elif type(tree) is ast.FloorDiv:
        return '//'
    elif type(tree) is ast.For:
        # TODO. The (THING)s are tuples. You'll need to figure out 
        # which vars to use.
        # #projectNoStateDict #yoloswag
        item = code(tree.target)
        body = many_to_one(tree.body, after='(MODIFIED_VARS)')
        items = code(tree.iter)
        if len(tree.orelse) is not 0:
            raise NotImplementedError("'for-else' is not implemented.")
        output = '(lambda (MODIFIED_VARS): %s)(reduce((lambda (MOD_VARS_USED), %s: %s), %s, (MOD_VARS_USED)))' % (after, item, body, items)
        return output
    elif type(tree) is ast.FunctionDef:
        args, arg_names = code(tree.args) ## of the form ('lambda x, y, z=5, *args:', ['x','y','z','args'])
        body = many_to_one(tree.body)
        ## The below commented out as part of #projectNoStateDict
        # body = assignment_component(body, '__d.'+',__d.'.join(arg_names), ','.join(arg_names)) ## apply lets for d.arguments
        function_code = args + body
        if len(tree.decorator_list) > 0:
            for decorator in tree.decorator_list:
                function_code = "%s(%s)" % (code(decorator), function_code)
        return assignment_component(after, tree.name, function_code)
    elif type(tree) is ast.arguments:
        ## return something of the form ('lambda x, y, z=5, *args:', ['x','y','z','args'])
        padded_defaults = [None]*(len(tree.args)-len(tree.defaults)) + tree.defaults
        arg_names = [arg.id for arg in tree.args]
        args = zip(padded_defaults, tree.args)
        args = [a.id if d is None else a.id+"="+code(d) for (d,a) in args]
        if tree.vararg is not None:
            args += ["*" + tree.vararg]
            arg_names += [tree.vararg]
        if tree.kwarg is not None:
            args += ["**" + tree.kwarg]
            arg_names += [tree.kwarg]
        args = ",".join(args)
        return ("lambda %s:" % (args), arg_names)
    elif type(tree) is ast.GeneratorExp:
        return '%s' % (' '.join([code(tree.elt)] + [code(gen) for gen in tree.generators]))
    elif type(tree) is ast.Global:
        raise NotImplementedError("'global' is an open problem.")
    elif type(tree) is ast.Gt:
        return '>'
    elif type(tree) is ast.GtE:
        return '>='
    elif type(tree) is ast.If:
        test = code(tree.test)
        ## (MODIFIED_VARS) is a tuple containing the names of the modified variables in BOTH branches
        body = many_to_one(tree.body, after='__after((MODIFIED_VARS))')
        orelse = many_to_one(tree.orelse, after='__after((MODIFIED_VARS))')
        return "(lambda __after: %s if %s else %s)(lambda (MODIFIED_VARS): %s)" % (body, test, orelse, after)
    elif type(tree) is ast.IfExp:
        return "(%s if %s else %s)" % (code(tree.body), code(tree.test), code(tree.orelse))
    elif type(tree) is ast.Import:
        for alias in tree.names:
            if alias.asname is None:
                alias.asname = alias.name
            after = assignment_component(after, alias.asname, "__import__('%s')"%alias.name)
        return after
    elif type(tree) is ast.ImportFrom:
        raise NotImplementedError("'import-from' is an open problem.")
    elif type(tree) is ast.In:
        return ' in '
    elif type(tree) is ast.Index:
        return '%s' % code(tree.value)
    elif type(tree) is ast.Interactive:
        return INIT_CODE % many_to_one(child_nodes(tree))
    elif type(tree) is ast.Invert:
        return '~'
    elif type(tree) is ast.Is:
        return ' is '
    elif type(tree) is ast.IsNot:
        return ' is not '
    elif type(tree) is ast.LShift:
        return '<<'
    elif type(tree) is ast.keyword:
        return '%s=%s' % (tree.arg, code(tree.value))
    elif type(tree) is ast.Lambda:
        args, arg_names = code(tree.args)
        body = code(tree.body)
        body = assignment_component(body, ','.join(arg_names), ','.join(arg_names))
        return '(' + args + body + ')'
    elif type(tree) is ast.List:
        elts = [code(elt) for elt in tree.elts]
        return '[%s]' % (','.join(elts))
    elif type(tree) is ast.ListComp:
        return '[%s]' % (' '.join([code(tree.elt)] + [code(gen) for gen in tree.generators]))
    elif type(tree) is ast.Lt:
        return '<'
    elif type(tree) is ast.LtE:
        return '<='
    elif type(tree) is ast.Mod:
        return '%'
    elif type(tree) is ast.Module:
        ## Todo: look into sys.stdout instead
        return INIT_CODE % many_to_one(child_nodes(tree))
    elif type(tree) is ast.Mult:
        return '*'
    elif type(tree) is ast.Name:
        return tree.id
        #return '__d.'+tree.id
    elif type(tree) is ast.Not:
        return 'not '
    elif type(tree) is ast.NotEq:
        return '!='
    elif type(tree) is ast.NotIn:
        return ' not in '
    elif type(tree) is ast.Num:
        return str(tree.n)
    elif type(tree) is ast.Or:
        return ' or '
    elif type(tree) is ast.Pass:
        return after
    elif type(tree) is ast.Pow:
        return '**'
    elif type(tree) is ast.Print:
        to_print = ','.join([code(x) for x in tree.values])
        if after is not 'None':
            return '(lambda ___: %s)(__print(%s))' % (after, to_print) ## TODO: ensure ___ isn't taken
        else:
            return '__print(%s)' % to_print
    elif type(tree) is ast.RShift:
        return '>>'
    elif type(tree) is ast.Raise:
        raise NotImplementedError("'raise' is an open problem.")
    elif type(tree) is ast.Repr:
        return 'repr(%s)' % code(tree.value)
    elif type(tree) is ast.Return:
        return code(tree.value)
    elif type(tree) is ast.Set:
        return 'set(%s)' % tree.elts
    elif type(tree) is ast.SetComp:
        return '{%s}' % (' '.join([code(tree.elt)] + [code(gen) for gen in tree.generators]))
    elif type(tree) is ast.Slice:
        if tree.step is None:
            return '%s:%s' % (code(tree.lower), code(tree.upper))
        else:
            return '%s:%s:%s' % (code(tree.lower), code(tree.upper), code(tree.step))
    elif type(tree) is ast.Str:
        return repr(tree.s)
    elif type(tree) is ast.Sub:
        return '-'
    elif type(tree) is ast.Subscript:
        return '%s[%s]' % (code(tree.value), code(tree.slice))
    elif type(tree) is ast.Suite:
        return INIT_CODE % many_to_one(child_nodes(tree))
    elif type(tree) is ast.TryExcept:
        raise NotImplementedError("'try-except' is an open problem.")
    elif type(tree) is ast.TryFinally:
        raise NotImplementedError("'try-finally' is an open problem.")
    elif type(tree) is ast.Tuple:
        elts = [code(elt) for elt in tree.elts]
        if len(elts) is 0:
            return '()'
        elif len(elts) is 1:
            return '(%s,)' % elts[0]
        else:
            return '(%s)' % (','.join(elts))
    elif type(tree) is ast.UAdd:
        return '+'
    elif type(tree) is ast.USub:
        return '-'
    elif type(tree) is ast.UnaryOp:
        return '(%s%s)' % (code(tree.op), code(tree.operand))
    elif type(tree) is ast.While:
        test = code(tree.test)
        body = many_to_one(tree.body, after='__this((USED_VARS))')
        orelse = many_to_one(tree.orelse, after='__after((MODIFIED_VARS))')
        return "(__y(lambda __this: (lambda (USED_VARS): (lambda __after: %s if %s else %s)(lambda (MODIFIED_VARS): %s))))((USED_VARS))" % (body, test, orelse, after)
    elif type(tree) is ast.With:
        raise NotImplementedError("'with' is an open problem.")
    elif type(tree) is ast.Yield:
        raise NotImplementedError("'yield' is an open problem.")
    elif tree is None:
        return ""
    else:
        raise NotImplementedError('case %s was not caught.' % str(type(tree)))



# def used_vars(tree):
#     if type(tree) is ast.Add:
#     elif type(tree) is ast.And:
#     elif type(tree) is ast.Assert:
#     elif type(tree) is ast.Assign:
#     elif type(tree) is ast.Attribute:
#     elif type(tree) is ast.AugAssign:
#     elif type(tree) is ast.BinOp:
#     elif type(tree) is ast.BitAnd:
#     elif type(tree) is ast.BitOr:
#     elif type(tree) is ast.BitXor:
#     elif type(tree) is ast.BoolOp:
#     elif type(tree) is ast.Break:
#     elif type(tree) is ast.Call:
#     elif type(tree) is ast.ClassDef:
#     elif type(tree) is ast.Compare:
#     elif type(tree) is ast.comprehension:
#     elif type(tree) is ast.Continue:
#     elif type(tree) is ast.Delete:
#     elif type(tree) is ast.Dict:
#     elif type(tree) is ast.DictComp:
#     elif type(tree) is ast.Div:
#     elif type(tree) is ast.Ellipsis:
#     elif type(tree) is ast.Eq:
#     elif type(tree) is ast.ExceptHandler:
#     elif type(tree) is ast.Exec:
#     elif type(tree) is ast.Expr:
#     elif type(tree) is ast.Expression:
#     elif type(tree) is ast.ExtSlice:
#     elif type(tree) is ast.FloorDiv:
#     elif type(tree) is ast.For:
#     elif type(tree) is ast.FunctionDef:
#     elif type(tree) is ast.arguments:
#     elif type(tree) is ast.GeneratorExp:
#     elif type(tree) is ast.Global:
#     elif type(tree) is ast.Gt:
#     elif type(tree) is ast.GtE:
#     elif type(tree) is ast.If:
#     elif type(tree) is ast.IfExp:
#     elif type(tree) is ast.Import:
#     elif type(tree) is ast.ImportFrom:
#     elif type(tree) is ast.In:
#     elif type(tree) is ast.Index:
#     elif type(tree) is ast.Interactive:
#     elif type(tree) is ast.Invert:
#     elif type(tree) is ast.Is:
#     elif type(tree) is ast.IsNot:
#     elif type(tree) is ast.LShift:
#     elif type(tree) is ast.keyword:
#     elif type(tree) is ast.Lambda:
#     elif type(tree) is ast.List:
#     elif type(tree) is ast.ListComp:
#     elif type(tree) is ast.Lt:
#     elif type(tree) is ast.LtE:
#     elif type(tree) is ast.Mod:
#     elif type(tree) is ast.Module:
#     elif type(tree) is ast.Mult:
#     elif type(tree) is ast.Name:
#     elif type(tree) is ast.Not:
#     elif type(tree) is ast.NotEq:
#     elif type(tree) is ast.NotIn:
#     elif type(tree) is ast.Num:
#     elif type(tree) is ast.Or:
#     elif type(tree) is ast.Pass:
#     elif type(tree) is ast.Pow:
#     elif type(tree) is ast.Print:
#     elif type(tree) is ast.RShift:
#     elif type(tree) is ast.Raise:
#     elif type(tree) is ast.Repr:
#     elif type(tree) is ast.Return:
#     elif type(tree) is ast.Set:
#     elif type(tree) is ast.SetComp:
#     elif type(tree) is ast.Slice:
#     elif type(tree) is ast.Str:
#     elif type(tree) is ast.Sub:
#     elif type(tree) is ast.Subscript:
#     elif type(tree) is ast.Suite:
#     elif type(tree) is ast.TryExcept:
#     elif type(tree) is ast.TryFinally:
#     elif type(tree) is ast.Tuple:
#     elif type(tree) is ast.UAdd:
#     elif type(tree) is ast.USub:
#     elif type(tree) is ast.UnaryOp:
#     elif type(tree) is ast.While:
#     elif type(tree) is ast.With:
#     elif type(tree) is ast.Yield:
#     else:
#         raise NotImplementedError('Case not caught: %s' % str(type(tree)))

    
# def modified_vars(tree):
#     if type(tree) is ast.Add:
#     elif type(tree) is ast.And:
#     elif type(tree) is ast.Assert:
#     elif type(tree) is ast.Assign:
#     elif type(tree) is ast.Attribute:
#     elif type(tree) is ast.AugAssign:
#     elif type(tree) is ast.BinOp:
#     elif type(tree) is ast.BitAnd:
#     elif type(tree) is ast.BitOr:
#     elif type(tree) is ast.BitXor:
#     elif type(tree) is ast.BoolOp:
#     elif type(tree) is ast.Break:
#     elif type(tree) is ast.Call:
#     elif type(tree) is ast.ClassDef:
#     elif type(tree) is ast.Compare:
#     elif type(tree) is ast.comprehension:
#     elif type(tree) is ast.Continue:
#     elif type(tree) is ast.Delete:
#     elif type(tree) is ast.Dict:
#     elif type(tree) is ast.DictComp:
#     elif type(tree) is ast.Div:
#     elif type(tree) is ast.Ellipsis:
#     elif type(tree) is ast.Eq:
#     elif type(tree) is ast.ExceptHandler:
#     elif type(tree) is ast.Exec:
#     elif type(tree) is ast.Expr:
#     elif type(tree) is ast.Expression:
#     elif type(tree) is ast.ExtSlice:
#     elif type(tree) is ast.FloorDiv:
#     elif type(tree) is ast.For:
#     elif type(tree) is ast.FunctionDef:
#     elif type(tree) is ast.arguments:
#     elif type(tree) is ast.GeneratorExp:
#     elif type(tree) is ast.Global:
#     elif type(tree) is ast.Gt:
#     elif type(tree) is ast.GtE:
#     elif type(tree) is ast.If:
#     elif type(tree) is ast.IfExp:
#     elif type(tree) is ast.Import:
#     elif type(tree) is ast.ImportFrom:
#     elif type(tree) is ast.In:
#     elif type(tree) is ast.Index:
#     elif type(tree) is ast.Interactive:
#     elif type(tree) is ast.Invert:
#     elif type(tree) is ast.Is:
#     elif type(tree) is ast.IsNot:
#     elif type(tree) is ast.LShift:
#     elif type(tree) is ast.keyword:
#     elif type(tree) is ast.Lambda:
#     elif type(tree) is ast.List:
#     elif type(tree) is ast.ListComp:
#     elif type(tree) is ast.Lt:
#     elif type(tree) is ast.LtE:
#     elif type(tree) is ast.Mod:
#     elif type(tree) is ast.Module:
#     elif type(tree) is ast.Mult:
#     elif type(tree) is ast.Name:
#     elif type(tree) is ast.Not:
#     elif type(tree) is ast.NotEq:
#     elif type(tree) is ast.NotIn:
#     elif type(tree) is ast.Num:
#     elif type(tree) is ast.Or:
#     elif type(tree) is ast.Pass:
#     elif type(tree) is ast.Pow:
#     elif type(tree) is ast.Print:
#     elif type(tree) is ast.RShift:
#     elif type(tree) is ast.Raise:
#     elif type(tree) is ast.Repr:
#     elif type(tree) is ast.Return:
#     elif type(tree) is ast.Set:
#     elif type(tree) is ast.SetComp:
#     elif type(tree) is ast.Slice:
#     elif type(tree) is ast.Str:
#     elif type(tree) is ast.Sub:
#     elif type(tree) is ast.Subscript:
#     elif type(tree) is ast.Suite:
#     elif type(tree) is ast.TryExcept:
#     elif type(tree) is ast.TryFinally:
#     elif type(tree) is ast.Tuple:
#     elif type(tree) is ast.UAdd:
#     elif type(tree) is ast.USub:
#     elif type(tree) is ast.UnaryOp:
#     elif type(tree) is ast.While:
#     elif type(tree) is ast.With:
#     elif type(tree) is ast.Yield:
#     else:
#         raise NotImplementedError('Case not caught: %s' % str(type(tree)))

## TODO same for modified_vars


## The entry point for everything.
def to_one_line(original):
    ## original :: string
    ## :: string
    global INIT_CODE

    original = original.strip()

    ## If there's only one line anyways, be lazy
    if len(original.splitlines()) == 1:
        return original

    t = ast.parse(original)
    INIT_CODE = get_init_code(t)

    return code(t)


# def has_single_print(tree):
#     ## TODO analysis for this
#     ## Return (True, ASTExpressionNode) if there is a single print (where ASTNode is the thing to be printeeee---
#     ## wait what if it's in a function k nevermind
#     return (False, None)





DEBUG = True ## TODO: Use command line arg instead



if __name__ == '__main__':
    if len(sys.argv) <= 1:
        print "Usage: python main.py inputfilename [outputfilename]"
    else:
        infilename = sys.argv[1]

        if len(sys.argv) >= 3:
            outfilename = sys.argv[2]
        else:
            if ".py" in infilename:
                outfilename = ".ol.py".join(infilename.rsplit(".py", 1))
            else:
                outfilename = infilename + ".ol.py"
            print "Writing to %s" % outfilename

        infi = open(infilename, 'r')
        outfi = open(outfilename, 'w')

        original = infi.read().strip()
        onelined = to_one_line(original)
        outfi.write(onelined+"\n")

        if DEBUG:
            print '--- ORIGINAL ---------------------------------'
            print original
            print '----------------------------------------------'
            try:
                exec(original)
            except Exception as e:
                print e
            print '--- ONELINED ---------------------------------'
            print onelined
            print '----------------------------------------------'
            try:
                exec(onelined)
            except Exception as e:
                print e
