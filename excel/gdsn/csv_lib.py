# -*- coding: utf-8 -*-
import csv, codecs, cStringIO


class UTF8Recoder(object):
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")


class UnicodeDictReader(object):
    def __init__(self, f, dialect="excel", encoding="utf-8", *args, **kwds):
        self._fieldnames = None
        self.reader = csv.reader(UTF8Recoder(f, encoding), dialect, *args, **kwds)
        self.dialect = dialect
        self.line_num = 0

    def __iter__(self):
        return self

    @property
    def fieldnames(self):
        if self._fieldnames is None:
            self._fieldnames = []
            try:
                fns = self.reader.next()
                for fn in fns:
                    self._fieldnames.append(unicode(fn.replace(" ", "_"), "utf-8"))
            except StopIteration:
                pass
        self.line_num = self.reader.line_num
        return self._fieldnames

    def next(self):
        if self.line_num == 0:
            # Used only for its side effect.
            self.fieldnames
        row = self.reader.next()
        self.line_num = self.reader.line_num

        # unlike the basic reader, we prefer not to return blanks,
        # because we will typically wind up with a dict full of None
        # values
        while row == []:
            row = self.reader.next()
        urow = [unicode(s, "utf-8") for s in row]
        d = dict(zip(self.fieldnames, urow))
        return d


class UnicodeDictWriter(object):
    def __init__(self, f, fieldnames, restval="", extrasaction="raise",
                 dialect="excel", encoding="utf-8", *args, **kwds):
        self.fieldnames = fieldnames    # list of keys for the dict
        self.restval = restval          # for writing short dicts
        if extrasaction.lower() not in ("raise", "ignore"):
            raise ValueError\
                  ("extrasaction (%s) must be 'raise' or 'ignore'" %
                   extrasaction)
        self.extrasaction = extrasaction
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect, *args, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writeheader(self):
        header = dict(zip(self.fieldnames, self.fieldnames))
        self.writerow(header)

    def _dict_to_list(self, rowdict):
        if self.extrasaction == "raise":
            wrong_fields = [k for k in rowdict if k not in self.fieldnames]
            if wrong_fields:
                raise ValueError("dict contains fields not in fieldnames: "
                                 + ", ".join([repr(x) for x in wrong_fields]))
        return [rowdict.get(key, self.restval) for key in self.fieldnames]

    def writerow(self, rowdict):
        row = []
        for s in self._dict_to_list(rowdict):
            try:
                row.append(s.encode("utf-8"))
            except Exception as e:
                row.append(s)
        self.writer.writerow(row)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rowdicts):
        for rowdict in rowdicts:
            self.writerow(rowdict)
