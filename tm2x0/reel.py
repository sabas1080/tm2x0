class Reel():
    def __init__(self,
                 reel_number=None,
                 stack_x_offset=None,
                 stack_y_offset=None,
                 feed_spacing=None,
                 height=0,
                 comment=None,
                 rotation=0):
        self.reel_number = reel_number
        self.stack_x_offset = stack_x_offset
        self.stack_y_offset = stack_y_offset
        self.feed_spacing = feed_spacing
        self.height = height
        self.comment = comment
        self.rotation = rotation

    def __repr__(self):
        return "<Reel {0}>".format(self.reel_number)