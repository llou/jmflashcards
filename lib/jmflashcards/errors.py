from traceback import format_exception
class JMFCError(Exception): pass

# Run comand error
class JMFCCommandError(JMFCError): 
    def __init__(self, command, path, rc, stdout, stderr):
        self.command = command
        self.path = path
        self.rc = rc
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        res = ["Error %d running command: '%s'" % (self.rc, self.command)]
        if not self.path is None:
            res.append("On path '%s'" % self.path)
        if self.stdout:
            res.append("Returned on stdout:\n%s" % self.stdout)
        if self.stderr:
            res.append("Returned on stderr:\n%s" % self.stderr)
        return "\n".join(res)

# Parsing errors

class JMFCEParsingError(JMFCError):
    pass

class JMFCParsingEntriesError(JMFCEParsingError):
    divider_symbol = "."
    divider_symbol_count = 70
    divider_line = "\n" + divider_symbol_count * divider_symbol + "\n"

    def __init__(self, flashcard, errors):
        self.flashcard = flashcard
        self.errors = errors

    def _format_exception(self, e_type, e_value, traceback):
        if issubclass(e_type, JMFCError):
            return str(e_value)
        else:
            return "\n".join(format_exception(e_type, e_value, traceback))

    def __str__(self):
        reference = self.flashcard.reference
        header = "Error parsing flashcard '%s' entries:" % reference
        error_msgs = [ self._format_exception(*e) for e in self.errors ]
        error_msgs.insert(0, header)
        return self.divider_line.join(error_msgs)

class JMFCEntryError(JMFCEParsingError):
    header_template = "Error handling entry %d:"

    def __init__(self, entry, msg):
        self.entry = entry
        self.msg = msg

    def _get_header_template_args(self):
        return (self.entry.index, )

    def _get_header(self):
        return self.header_template % self._get_header_template_args()

    def __str__(self):
        header = self._get_header()
        return "%s\n%s" % (header, self.msg)

class JMFCEntrySideError(JMFCEntryError):
    header_template = "Error handling entry %d %s '%s':"

    def __init__(self, side, msg):
        self.side = side
        self.msg = msg

    def _get_header_template_args(self):
        return (self.side.entry.index, self.side.side, self.side.raw_text)


# Flashcards deluxe error
class FCDError(JMFCError): pass
