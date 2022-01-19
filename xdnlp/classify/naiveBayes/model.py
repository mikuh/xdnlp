from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import BernoulliNB
import os
import joblib
import time
import numpy as np
import json
from xdnlp.utils import default_logger as logging
from xdnlp.utils import read_csv_row


class BernouliNB(object):
    def __init__(self, alpha=0.1, is_train=True, preprocess=None):
        self.vec_model = CountVectorizer(lowercase=False, token_pattern=r"(?u)[^ \n]+")
        self.classification_model = BernoulliNB(alpha=alpha)
        self.__save_path = "./models/" + str(int(time.time()))
        self.accuracy = 0.0
        if preprocess is None:
            self.preprocess = lambda x: x.split()
        else:
            self.preprocess = preprocess
        if not os.path.exists(self.__save_path) and is_train:
            os.makedirs(self.__save_path)

    def fit(self, inputs, targets):
        inputs = self.vec_model.fit_transform(inputs)
        self.classification_model.fit(inputs, targets)
        self.accuracy = self.__score(inputs, targets)
        logging.info(f"\nAccuracy: {self.accuracy}")

        self.__save()
        logging.info(f"Save model and parameters, at: {self.__save_path}")

    def __score(self, inputs, targets):
        return self.classification_model.score(inputs, targets)

    def __save(self):
        joblib.dump(self.vec_model, os.path.join(self.__save_path, "vectorizer.model"))
        joblib.dump(self.classification_model, os.path.join(self.__save_path, "clf_bernoulli_nb.model"))
        joblib.dump(self.preprocess, os.path.join(self.__save_path, "preprocess.model"))
        self.export_parameter()

    def load(self, model_path):
        self.vec_model = joblib.load(os.path.join(model_path, "vectorizer.model"))
        self.classification_model = joblib.load(os.path.join(model_path, "clf_bernoulli_nb.model"))

    def load_data(self, filename):
        targets = []
        inputs = []
        for row in read_csv_row(filename):
            if len(row) == 3:
                for _ in range(int(row[2])):
                    targets.append(row[0])
                    inputs.append(self.preprocess(row[1]))
        return inputs, targets

    def predict(self, inputs):
        count_vec = self.vec_model.transform(inputs)
        ret = list(self.classification_model.predict(count_vec))
        return ret

    def export_parameter(self):
        features = self.vec_model.get_feature_names()
        vocab = self.vec_model.vocabulary_
        classes_ = self.classification_model.classes_
        pos_log_prob = self.classification_model.feature_log_prob_
        neg_prob = np.log(1 - np.exp(self.classification_model.feature_log_prob_))
        del_prob = (pos_log_prob - neg_prob).T
        class_log_prob = self.classification_model.class_log_prior_

        json_data = {
            "Classes": classes_.tolist(),
            "Features": features,
            "Vocab": {k: int(v) for k, v in vocab.items()},
            "DelProb": del_prob.tolist(),
            "NegProb": neg_prob.tolist(),
            "ClassLogProb": class_log_prob.tolist()
        }

        with open(os.path.join(self.__save_path, "model.json"), 'w', encoding='utf-8') as f:
            json.dump(json_data, f)
