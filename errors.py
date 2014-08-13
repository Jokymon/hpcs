class CompilationError(Exception):
    def __init__(self, message, file_name, line, column):
        self.file_name = file_name
        self.line = line
        self.column = column
        full_message = "%s:%u:%u: %s" % (file_name, line, column, message)
        Exception.__init__(self, full_message)
