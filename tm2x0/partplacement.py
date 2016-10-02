class PartPlacement():
    """PartPlacement is the general, objecty thing that a PartPlacementInstruction corresponds to.

    It is similar to Reel()."""
    def __init__(self,
                 reference,
                 x,
                 y,
                 rotation=0,
                 height=None,
                 footprint=None,
                 value=None,
                 comment=None,
                 reel=None,
                 head=1
    ):
        self.reel = reel
        self.reference = reference
        self.value = value
        self.footprint = footprint
        self.x = x
        self.y = y
        self.height = height
        self.rotation = rotation
        self.comment = comment
        self.head=head


    def __repr__(self):
        out = "<{0}".format(self.footprint)
        if self.value:
            out += " @ {0}>".format(self.value)
        else:
            out += ">"
        return out