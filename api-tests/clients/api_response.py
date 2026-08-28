class ApiResponse:

    def __init__(self, response):
        self.status_code = response.status_code
        self.text = response.text
        self.headers = response.headers

        try:
            self.body = response.json()
        except ValueError:
            self.body = response.text
