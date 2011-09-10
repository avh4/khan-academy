import urllib
import urllib2
import urlparse
import cookielib
import json

TEST_GAE_URL = "http://localhost:8080/gae_bingo/tests/run_step"

last_opener = None

def test_response(step, data={}, use_last_cookies=False, bot=False):

    if not use_last_cookies or last_opener is None:
        cj = cookielib.CookieJar()
        last_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))

        if bot:
            last_opener.addheaders = [('User-agent', 'monkeysmonkeys Googlebot monkeysmonkeys')]

    data["step"] = step

    req = last_opener.open("%s?%s" % (TEST_GAE_URL, urllib.urlencode(data)))

    try:
        response = req.read()
    finally:
        req.close()

    return json.loads(response)

def run_tests():

    # Delete all experiments (response should be count of experiments left)
    assert(test_response("delete_all") == 0)

    # Refresh bot's identity record so it doesn't pollute tests
    assert(test_response("refresh_identity_record", bot=True) == True)

    # Participate in experiment A, check for correct alternative values being returned,
    for i in range(0, 20):
        assert(test_response("participate_in_monkeys") in [True, False])

    # Identify as a bot a couple times (response should stay the same)
    bot_value = None
    for i in range(0, 5):
        value = test_response("participate_in_monkeys", bot=True)

        if bot_value is None:
            bot_value = value

        assert(value == bot_value)

    # Check total participants in A (1 extra for bots)
    assert(test_response("count_participants_in", {"experiment_name": "monkeys"}) == 21)
    
    # Participate in experiment B (responses should be "a" "b" or "c")
    for i in range(0, 15):
        assert(test_response("participate_in_gorillas") in ["a", "b", "c"])

    # Participate in experiment A, using cookies half of the time to maintain identity
    for i in range(0, 20):
        assert(test_response("participate_in_monkeys", use_last_cookies=(i % 2 == 0)) in [True, False])

    # Check total participants in A
    assert(test_response("count_participants_in", {"experiment_name": "monkeys"}) == 31)

    # Participate and convert in experiment A, using cookies to tie participation to conversions,
    # tracking conversions-per-alternative
    dict_conversions = {}
    for i in range(0, 35):
        alternative = test_response("participate_in_monkeys")
        assert(test_response("convert_in", {"conversion_name": "monkeys"}, use_last_cookies=True) == True)

        if not alternative.number in dict_conversions:
            dict_conversions[alternative.number] = 0
        dict_conversions[alternative.number] += 1

    # Check total conversions-per-alternative in A
    assert(35 == reduce(lambda a, b: a + b, map(lambda key: dict_conversions[key], dict_conversions)))
    assert(test_response("count_conversions_in", {"experiment_name": "monkeys"}) == dict_conversions)

    # Participate in experiment B N times, using cookies to maintain identity
    #
    # Make sure alternatives for B are stable per identity
    #
    # Participate in experiment C N times, which is a multi-conversion experiment
    #
    # Convert in *one* of C's conversions a couple times
    #
    # Make sure conversion counts are correct for both of C's conversion experiments
    #
    # End experiment C, choosing a short-circuit alternative
    #
    # Make sure short-circuited alternatives for both of C's experiments are set appropriately
    #
    # Participate in experiment D N times, keeping track of alternative returned count.
    #
    # Make sure weighted alternatives work -> should be a < b < c < d < e, but they should all exist.
    #
    # Check experiments count

if __name__ == "__main__":
    run_tests()


