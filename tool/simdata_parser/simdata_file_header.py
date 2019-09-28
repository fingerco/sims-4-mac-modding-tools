class SimdataFileHeader:
    def __init__(self):
        self.mnFileIdentifier = None        # Should always be 'DATA'
        self.mnVersion = None               # Base game version is 0x100
        self.mnTableHeaderOffset = None     # Offset of table header data
        self.mnSchemaOffset = None          # Offset of schema data
        self.mnNumSchemas = None            # Number of schemas

    def __str__(self):
        print("Simdata File Header: \n" +
            f"  mnFileIdentifier: {self.mnFileIdentifier}\n" +
            f"  mnVersion: {self.mnVersion}\n" +
            f"  mnTableHeaderOffset: {self.mnTableHeaderOffset}\n" +
            f"  mnSchemaOffset: {self.mnSchemaOffset}\n" +
            f"  mnNumSchemas: {self.mnNumSchemas}\n" +
        "\n")
