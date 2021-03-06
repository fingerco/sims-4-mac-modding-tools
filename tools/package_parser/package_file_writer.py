import zlib
import re
import binascii
import struct
from .package_file import PackageFile
from .package_file_header import PackageFileHeader
from .package_version import PackageVersion
from .package_flags import PackageFlags
from .package_index_entry import PackageIndexEntry
from .package_errors import IncorrectFilename

class PackageFileWriter:
    def __init__(self):
        self.headers = PackageFileHeader()
        self.headers.mnFileIdentifier = 'DBPF'
        self.headers.mnFileVersion = PackageVersion(major=2, minor=1)
        self.headers.mnUserVersion = PackageVersion(major=0, minor=0)
        self.headers.mnIndexRecordPositionLow = 0
        self.headers.mnIndexRecordPosition = 0
        self.headers.constantInstanceIdEx = 0

        self.headers.flags = PackageFlags(
            constantType        = 0,
            constantGroup       = 0,
            constantInstanceEx  = 0,
            reserved            = 0
        )

        self.index_entries = []
        self.records = []
        self.record_data = bytearray([])

    def add_writer(self, writer):
        self.add_resource(
            struct.pack('>I', writer.resource_type),
            struct.pack('>I', writer.resource_group),
            struct.pack('>Q', writer.resource_instance_id),
            writer.to_bytearray()
        )


    def add_resource_file(self, file_path):
        filename = file_path.split('/')[-1]
        parsed_filename = re.match("0x(.*?)_0x(.*?)_0x(.*?)$", filename)
        if parsed_filename:
            parsed_data = parsed_filename.groups()

            resource_type = binascii.a2b_hex(parsed_data[0])
            resource_group = binascii.a2b_hex(parsed_data[1])

            instance_id_str = parsed_data[2].split('.')[0]
            resource_name = None
            parsed_instance_id = re.match("(.*?)_(.*?)$", instance_id_str)
            if parsed_instance_id:
                instance_id_str = parsed_instance_id.groups()[0]
                resource_name = parsed_instance_id.groups()[1]

            resource_instance_id = binascii.a2b_hex(instance_id_str)

            raw_data = None
            with open(file_path, mode='rb') as f:
                raw_data = f.read()

            return self.add_resource(resource_type, resource_group, resource_instance_id, raw_data)
        else:
            raise IncorrectFilename()


    def add_resource(self, type, group, instance_id, data):
        compressed_data = zlib.compress(data)

        index_entry = PackageIndexEntry(self.headers.flags)
        index_entry.load_resource(type, group, instance_id, data, compressed_data)
        index_entry.mbExtendedCompressionType = 1
        index_entry.mnCompressionType = "ZLIB"
        index_entry.mnCommitted = 1

        index_entry.mnPosition = self.headers.size() + len(self.record_data)
        self.record_data.extend(compressed_data)

        self.index_entries.append(index_entry)
        self.records.append(compressed_data)

    def to_bytearray(self):
        self.headers.mnIndexRecordEntryCount = len(self.index_entries)
        self.headers.mnIndexRecordPosition = self.headers.size() + len(self.record_data)

        index_record_size = 0
        for index_entry in self.index_entries:
            index_record_size += index_entry.size()

        self.headers.mnIndexRecordSize = index_record_size + self.headers.flags.size()

        print(self.headers)

        raw_data = bytearray([])
        raw_data.extend(self.headers.to_bytearray())
        raw_data.extend(self.record_data)
        raw_data.extend(self.headers.flags.to_bytearray())

        for index_entry in self.index_entries:
            raw_data.extend(index_entry.to_bytearray())

        return raw_data
