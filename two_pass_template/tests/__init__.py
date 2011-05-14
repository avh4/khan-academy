import logging
import StringIO

from two_pass_template import two_pass_variable, two_pass_handler
import request_handler

class TwoPassTemplateTest(request_handler.RequestHandler):

    @two_pass_variable()
    def sheep(self, monkey):
        return monkey + self.request_int("inc", default=1)

    @two_pass_variable()
    def donkey(self, gorilla):
        return gorilla + self.request_int("inc", default=1)

    @two_pass_variable()
    def zebras(self):
        return "hrm"

    @two_pass_handler()
    def test_simple(self):
        template_values = {
            "monkey": "gorilla"
        }
        return ("two_pass_template/tests/test_simple.html", template_values)

    @two_pass_variable()
    def unsafe_string_two(self):
        return "<script>"

    @two_pass_handler()
    def test_unsafe(self):
        template_values = {
            "unsafe_string": "{{<script>}}",
            "unsafe_string_two": self.unsafe_string_two(),
        }
        return ("two_pass_template/tests/test_unsafe.html", template_values)

    @two_pass_handler()
    def test_complex(self):

        monkey = 5
        gorilla = 6

        template_values = {
            "sheep": self.sheep(monkey),
            "donkey": self.donkey(gorilla),
            "zebras": self.zebras(),
            "monkey": "ooh ooh aah aah",
            "monkeys": ["a", "b"],
            "unsafe_string": "unsafe_{{monkey}}"
        }

        return ("two_pass_template/two_pass_test.html", template_values)

    def get(self):

        self.response.out = StringIO.StringIO()
        self.test_simple(first_pass_override=True)
        result = self.response.out.getvalue().strip()
        assert(result == "hello gorilla goodbye")

        self.response.out = StringIO.StringIO()
        self.test_simple()
        result = self.response.out.getvalue().strip()
        assert(result == "hello gorilla goodbye")

        self.response.out = StringIO.StringIO()
        self.test_unsafe()
        result = self.response.out.getvalue().strip()
        assert(result == "&#123;&#123;&lt;script&gt;&#125;&#125;&lt;script&gt;")

        self.response.out = StringIO.StringIO()
        self.test_unsafe(first_pass_override=True)
        result = self.response.out.getvalue().strip()
        assert(result == "&#123;&#123;&lt;script&gt;&#125;&#125;{{unsafe_string_two|escape}}")

        self.response.out = StringIO.StringIO()
        self.response.out.write("All tests passed.")

