import argparse, os, sys

NO_VAL = object()

def parse_cli_args():
    # TODO: Better help and description messages
    # TODO: fix argparse usage message
    parser = argparse.ArgumentParser(description='Process some CLI arguments.')
    parser.add_argument('-f', '--files', type=str, nargs='*', help='The input file paths')
    parser.add_argument('-o', '--output', type=str, nargs='?', help='Mapping file to create')
    parser.add_argument('-x', '--execute', type=str, nargs='?', help='Execute on given mapping', const=NO_VAL)
    parser.add_argument('-ox', '--mapex', type=str, nargs='?', help='Map and execute on mapping', const=NO_VAL)
    parser.add_argument('-u', '--undo', type=str, nargs='?', help='Undoes given mapping', const=NO_VAL)
    parser.add_argument('-s', '--structure', type=str, nargs='?', help='Structure to generate name from', default='[SubjectDescription]_[MainColor/ColorScheme]_[StyleOrFeel]_[CompositionElement].jpg')
    parser.add_argument('-r', '--retries', type=int, help='Set number of validation and error retries', default=3)
    parser.add_argument('-K', '--skip-errors', action='store_true', help='Skip errors')
    parser.add_argument('-k', '--skip-validation', action='store_true', help='Skip errors')

    # if flag with value, equals value
    # if flag with no value, equals const value
    # if flag not used, equals None


    # capture initial defaults before parsing
    # this is for the below 'hack'
    defaults = {action.dest: action.default for action in parser._actions}
    
    args = parser.parse_args()
    args_dict = vars(args)

    ####################################################################################
    ### NOTE: this section is here to make sure if -u is used, its by itself
    ###       It is a bit hacky and hard to understand, but it seems there is
    ###       no way to do this thats not hacky or unclear
    if args.undo is not None:
        # Check if any other arg changed from default
        non_default_args = [arg for arg in args_dict if args_dict[arg] != defaults[arg]]
    
        # Remove checked key since we don't need to check it against itself
        non_default_args.remove('undo')
    
        # If any other arguments changed, error
        if non_default_args:
            parser.error('-u/--undo must not be used with any other arguments.')
    ####################################################################################

    if args.files is not None and len(args.files) == 0:
        parser.error("-f/--files requires a value")

    if args.output is not None and args.execute is not None:
        parser.error("instead of using -o/--output along with -x/--execute, use -ox/--mapex")
        
    if args.mapex is not None:
        if args.output is not None or args.execute is not None:
            parser.error("-ox/--mapex should be used without -o/--output or -x/--execute")

        args.output = args.mapex
        args.execute = args.mapex

        
    if args.output is not None and args.files is None:
        parser.error('-o/--output must be used with -f/--files')

    if args.structure is None:
        parser.error('used -s/--structure with no value')

    supported_ext = ['.png', '.jpeg', '.jpg', '.webp', '.gif']


    #
    # get absolute paths where we need them
    #
    if args.files is not None:
        args.files = [os.path.abspath(path) for path in args.files]
        clean_paths = args.files.copy()

        for image_path in args.files:
            if os.path.isdir(image_path):
                print("{} is directory, skipping...".format(image_path))
                clean_paths.remove(image_path)
            elif not os.path.exists(image_path):
                parser.error("{} doesn't exist".format(image_path))

        for image_path in clean_paths:
            _, image_ext = os.path.splitext(image_path)
            if image_ext not in supported_ext:
                parser.error('Filetype {} not supported'.format(image_ext))
        args.files = clean_paths

    if args.output is not None and args.output != NO_VAL:
        args.output = os.path.abspath(args.output)

    if args.execute is not None and args.execute != NO_VAL:
        args.execute = os.path.abspath(args.execute)

    if args.undo is not None and args.undo != NO_VAL:
        args.undo = os.path.abspath(args.undo)
    
    return args
