class ServerResource(object):
    def __init__(self, id, website, resource_origin, resource_new, locations, hash):
        self.id = id
        self.website = website
        self.resource_origin = resource_origin
        self.resource = resource_new
        self.locations = locations
        self.hash = hash

    def get_resource(self):
        return self


if __name__ == '__main__':
    serverR = ServerResource(1, "google.com", "a.js", "b.js", "[1.1.1.1,2.2.2.2]", "fdasf")

    b = serverR.get_resource()
    print(b.hash)
