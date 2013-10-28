import unittest
import os
import flask

from flask_mab import BanditMiddleware
import flask_mab.storage
from flask_mab.bandits import EpsilonGreedyBandit

    
def makeBandit():
    bandit = EpsilonGreedyBandit(0.1)
    bandit.add_arm("green","#00FF00")
    bandit.add_arm("red","#FF0000")
    return bandit


class MABTestCase(unittest.TestCase):

    def setUp(self):
        banditStorage = flask_mab.storage.JSONBanditStorage('./bandits.json')
        app = flask.Flask('test_app')
        mab = flask_mab.BanditMiddleware(app,banditStorage)
        mab.add_bandit('color_button', makeBandit())

        app.debug = True

        @app.route("/")
        def root():
            return flask.make_response("Hello!")

        @app.route("/show_btn")
        def assign_arm():
            assigned_arm = mab.suggest_arm_for("color_button",True)
            return flask.make_response("arm")

        self.app = app
        self.mab = mab
        self.app_client = app.test_client()

    def test_routing(self):
        rv = self.app_client.get("/")
        assert "Hello" in rv.data

    def test_suggest(self):
        rv = self.app_client.get("/show_btn")
        self.mab.debug_headers = True
        assert "MAB-Debug" in rv.headers.keys()
        chosen_arm = self.get_arm(rv.headers)["color_button"]
        assert self.mab["color_button"][chosen_arm]["pulls"] > 0

    def get_arm(self,headers):
        key_vals = [h.strip() for h in headers["MAB-Debug"].split(';')[1:]]
        return dict([tuple(tup.split(":")) for tup in key_vals])

if __name__ == '__main__':
    unittest.main()
