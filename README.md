# xdnlp
A highly efficient and easy-to-use natural language processing library.

# Install
```shell script
pip install xdnlp
```

or

```shell
git clone https://github.com/mikuh/xdnlp
pip install ./xdnlp/
```

# APIS
There are still some function introductions that have not been written for the time being, wait for my follow-up update.

## Text
### Normalize
Character normalization.
```python
from xdnlp import Text
text = Text()
text.normalize("降龍⑴⑧掌")  # 降龍⑴⑧掌 -> 降龙18掌 
```

### Keyword Extract
Extract keywords from sentence.
```python
from xdnlp import Text
text = Text()
text.add_keywords_from_list(["c++", 'python', 'java', 'javascript'])
text.extract_keywords("小明学习了python c++ javascript", longest_only=True)
# return  ["python", 'c++', 'javascript']

# batch mode
text.batch_extract_keywords(["小明学会了c++", "python和c++有什么区别", "Javascript和java是同一个东西吗"])
# return [['c++'], ['python', 'c++'], ['java']]
```

### Keyword Replace
Replace keywords in sentence.
```python
from xdnlp import Text
text = Text()
text.add_keywords_replace_map_from_dict({
    "java": "golang",
    "javascript": "node"
})
text.replace_keywords("小明学习了python c++ javascript")
# return 小明学习了python c++ node

# batch mode
text.batch_replace_keywords(["小明学会了c++", "python和c++有什么区别", "javascript和java是同一个东西吗"])
# return ["小明学会了c++", "python和c++有什么区别", "node和golang是同一个东西吗"]
```

### Text clean
Remove extraneous characters from a sentence.
```python
from xdnlp import Text
text = Text()
text.clean("aaaaaaAAAAA9123123我是    中国人-=[]:<>aaa", max_repeat=2)
# return aa9123123我是 中国人 aa

# batch mode
text.batch_clean(["aaaaaaAAAAA9123123我是    中国人-=[]:<>aaa", "666666"], max_repeat=2) \
# return ["aa9123123我是 中国人 aa", '66']
```

### Text encode
A text encoder.
```python
from xdnlp import Text
text = Text()
text.encode("wo操你妈、フちqlフq、")
# return {'contact': 1, 'unknown': 1, 'specify': 0, 'length': 13, 'low_frequency': 0, 'zh_scale': 0.6153846153846154, 'en_num_scale': 0.0, 'zh_piece_scale': 0.6666666666666666, 'not_zh_piece_scale': 0, 'pinyin': 'wocaonima、フちqlフq、'}
```

### Text batch cut words
Batch cut words from a iterator
```python
from xdnlp import Text
import jieba

text = Text()
text_list = ["百战大佬 要不要来6线帮打打", "对呀，觉得后面的时间才是自己的",
             "亡者酋长头饰图纸很贵哟", "嗯,不懂,快凉了,哈哈,刚看到10月就抢了"] * 1000000
out = text.batch_cut(text_list, jieba, n_jobs=20, batch_size=1000)
# return [['百战', '大佬', ' ', '要', '不要', '来', '6', '线帮', '打打'], ['对', '呀', '，', '觉得', '后面', '的', '时间', '才', '是', '自己', '的'],...]
```

## Word Discover
Found vocabulary from massive text
```python
from xdnlp import WordDiscover
wd = WordDiscover()
wd.word_discover(["path/to/the.txt"], save_ngram=True)
```

## Classify


### TextCNN
```python
import os
import tensorflow as tf
from xdnlp.classify import TextCNN
from xdnlp.classify.utils import load_data_from_directory, get_vectorize_layer
max_features = 50000
max_len = 100
batch_size = 64
epochs = 20
data_dir = "path/to/your/data/dir"

train_ds, val_ds, test_ds, class_names = load_data_from_directory(data_dir, batch_size=batch_size)
vectorize_layer = get_vectorize_layer(max_features, max_len, train_ds)

model_config = dict(input_shape=(max_len,),
                    class_names=class_names,
                    model_dir="models",
                    vectorize_layer=vectorize_layer,
                    embedding_size=128,
                    hidden_size=256,
                    filter_sizes=[3, 4, 5],
                    num_filters=256,
                    dropout=0.2,
                    is_train=True)

model = TextCNN(**model_config)
model.train(train_ds, val_ds, 1)

# predict
model_save_path = "your model save path"

# load from ckpt
config = TextCNN.get_model_config(model_save_path)
vectorize_layer = get_vectorize_layer(config["max_features"], config["max_len"], vocabulary=config["vocabulary"])
model_config = dict(input_shape=(config["max_len"],),
                    vectorize_layer=vectorize_layer,
                    class_names=config["class_names"],
                    embedding_size=config["embedding_size"],
                    hidden_size=config["hidden_size"],
                    filter_sizes=config["filter_sizes"],
                    num_filters=config["num_filters"],
                    dropout=config["dropout"],
                    is_train=False)
    
model = TextCNN(**model_config)

# load from pb
model = tf.keras.models.load_model(os.path.join(model_save_path, "my_model"))
res = model(tf.constant(["这 什么 垃圾 游戏"]))
print(config["class_names"][tf.argmax(res[0]).numpy()])
```

### TextRNN
```python
from xdnlp.classify import TextRNN
from xdnlp.classify.utils import load_data_from_directory, get_vectorize_layer
import tensorflow.keras as keras
max_features = 50000
max_len = 100
batch_size = 64
data_dir = "path/to/your/data/dir"
model_dir = "dir/for/save/model"
embedding_size = 128
rnn_hidden_size = 256
fc_hidden_size = 128
num_layers = 2
dropout = 0.2
epochs = 2

train_ds, val_ds, test_ds, class_names = load_data_from_directory(data_dir, batch_size)
vectorize_layer = get_vectorize_layer(max_features, max_len, train_ds)

model = TextRNN(vectorize_layer=vectorize_layer,
                class_names=class_names,
                model_dir=model_dir,
                embedding_size=embedding_size,
                rnn_hidden_size=rnn_hidden_size,
                fc_hidden_size=fc_hidden_size,
                num_layers=num_layers,
                dropout=dropout,
                is_train=True)

model.train(train_ds, val_ds, epochs)
model.evaluate(test_ds)

# load from ckpt
model_config_path = "path/to/model_config"
checkpoint_path = "path/to/checkpoint/for/loading"
batch_size = 64
model_config = TextRNN.get_model_config(model_config_path)

vectorize_layer = get_vectorize_layer(model_config["max_features"],
                                        model_config["max_len"],
                                        vocabulary=model_config["vocabulary"])


model = TextRNN(vectorize_layer=vectorize_layer,
                class_names=model_config["class_names"],
                embedding_size=model_config["embedding_size"],
                rnn_hidden_size=model_config["rnn_hidden_size"],
                fc_hidden_size=model_config["fc_hidden_size"],
                num_layers=model_config["num_layers"],
                dropout=model_config["dropout"],
                is_train=False)

model.compile(optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy'])
model.load_weights(checkpoint_path)

# load from pb
model_save_path = "path/to/model/for/loading"
model = keras.models.load_model(model_save_path)
model.evaluate(test_ds)
```

### Bert or Albert classify
```python
from xdnlp.classify import BertClassify

handle_encoder = ""  # bert or albert pre train encoder,set local savedmodel dir or tfhub model url
handle_preprocess = ""  # bert  preprocess,set local savedmodel dir or tfhub model url
model = BertClassify(handle_encoder,
                     handle_preprocess,
                    categories=2)
# set train and test data dir
train_ds, val_ds, test_ds = model.load_data("../../bert/aclImdb/train", "../../bert/aclImdb/test", )
model.preview_train_data(train_ds)
model.preview_classify()
model.train(train_ds, val_ds)
```