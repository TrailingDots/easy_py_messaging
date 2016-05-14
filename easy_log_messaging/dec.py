
def fcnName(func):
    def wrapper(*func_args, **func_kwargs):
        print('=== test fcn: ' + func.__name__)
        return func(*func_args, **func_kwargs)
    return wrapper

@fcnName
def helper(blah):
    print 'hello ' + blah

if __name__ =='__main__':
    helper('zzzz')
    
