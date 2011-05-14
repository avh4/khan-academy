import logging
import string
import StringIO

import django.template as template
from two_pass_template import two_pass_variable, two_pass_handler
import request_handler

class TwoPassTemplateTest(request_handler.RequestHandler):

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

    @two_pass_variable()
    def sheep(self, monkey):
        return monkey + 1

    @two_pass_variable()
    def donkey(self, gorilla):
        return gorilla + 1

    @two_pass_variable()
    def zebras(self):
        return "hrm"

    @two_pass_handler()
    def test_complex(self):

        monkey = 5
        gorilla = 6

        template_values = {
            "sheep": self.sheep(monkey),
            "donkey": self.donkey(gorilla),
            "zebras": self.zebras(),
            "monkey": "on trees",
            "monkeys": ["a", "b"],
            "unsafe_string": "unsafe_{{monkey}}"
        }

        return ("two_pass_template/tests/test_complex.html", template_values)

    @two_pass_handler()
    def test_missing_variable(self):
        return ("two_pass_template/tests/test_complex.html", {})

    @staticmethod
    def assert_equal_no_whitespace(result, expected):
        for c in string.whitespace:
            result = result.replace(c, "")
            expected = expected.replace(c, "")
        assert(result == expected)

    def get(self):

        self.response.out = StringIO.StringIO()
        self.test_simple(first_pass_override=True)
        result = self.response.out.getvalue().strip()
        self.assert_equal_no_whitespace(result, "hello gorilla goodbye")

        self.response.out = StringIO.StringIO()
        self.test_simple()
        result = self.response.out.getvalue().strip()
        self.assert_equal_no_whitespace(result, "hello gorilla goodbye")

        self.response.out = StringIO.StringIO()
        self.test_unsafe()
        result = self.response.out.getvalue().strip()
        self.assert_equal_no_whitespace(result, "&#123;&#123;&lt;script&gt;&#125;&#125;&lt;script&gt;")

        self.response.out = StringIO.StringIO()
        self.test_unsafe(first_pass_override=True)
        result = self.response.out.getvalue().strip()
        self.assert_equal_no_whitespace(result, "&#123;&#123;&lt;script&gt;&#125;&#125;{{unsafe_string_two|escape}}")

        self.response.out = StringIO.StringIO()
        self.test_complex(first_pass_override=True)
        result = self.response.out.getvalue().strip()
        expected = """
            <html>
                <body>
                    unsafe_&#123;&#123;monkey&#125;&#125;
                    <script>var test = 'unsafe_\u007B\u007Bmonkey\u007D\u007D';</script>

                    {%if sheep%}
                        Test({{sheep}} vs. {{donkey}})
                        {%if monkeys%}
                            {%for a in monkeys%}
                                Grr?! {{monkey}}
                            {%endfor%}
                        {%endif%}
                        Nope
                    {%endif%}
                    
                        {{zebras|cut:zebras}}

                </body>
            </html>
        """
        self.assert_equal_no_whitespace(result, expected)

        self.response.out = StringIO.StringIO()
        self.test_complex()
        result = self.response.out.getvalue().strip()
        expected = """
            <html>
                <body>
                    unsafe_&#123;&#123;monkey&#125;&#125;
                    <script>var test = 'unsafe_\u007B\u007Bmonkey\u007D\u007D';</script>
                        Test(6 vs. 7)
                                Grr?! on trees
                                Grr?! on trees
                        Nope
                </body>
            </html>
        """
        self.assert_equal_no_whitespace(result, expected)

        self.response.out = StringIO.StringIO()
        caught = False
        try:
            self.test_missing_variable()
        except template.VariableDoesNotExist:
            caught = True
        assert(caught)

        self.response.out = StringIO.StringIO()
        self.response.out.write("All tests passed.")
