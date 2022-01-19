import tensorflow as tf
import os
from xdnlp.utils import default_logger as logging


def load_data_from_directory(_path: str, batch_size, validation_split=0.1, seed=123, label_mode='categorical',
                             train=True):
    """train_dir: the train data dir
      test_dir: the test data dir
      Just set the directory:
      ```
      main_directory/
      ...class_a/
      ......a_text_1.txt
      ......a_text_2.txt
      ...class_b/
      ......b_text_1.txt
      ......b_text_2.txt
      ```
      """
    train_ds = None
    val_ds = None
    class_names = None
    if train:
        train_ds = tf.keras.preprocessing.text_dataset_from_directory(
            os.path.join(_path, 'train'), batch_size=batch_size, validation_split=validation_split,
            subset='training', seed=seed, label_mode=label_mode)
        class_names = train_ds.class_names
        train_ds = train_ds.cache().prefetch(tf.data.AUTOTUNE)

        val_ds = tf.keras.preprocessing.text_dataset_from_directory(
            os.path.join(_path, 'train'), batch_size=batch_size, validation_split=validation_split,
            subset='validation', seed=seed, label_mode=label_mode)
        val_ds = val_ds.cache().prefetch(tf.data.AUTOTUNE)
    test_ds = tf.keras.preprocessing.text_dataset_from_directory(
        os.path.join(_path, 'test'), batch_size=batch_size, label_mode=label_mode)
    if class_names is None:
        class_names = test_ds.class_names
    test_ds = test_ds.cache().prefetch(tf.data.AUTOTUNE)
    logging.info(f"Load data from directory successfully, class_names: {class_names}")
    return train_ds, val_ds, test_ds, class_names


def get_vectorize_layer(max_features, max_len, train_ds: tf.data.Dataset = None,
                        vocabulary=None, output_mode='int', split='whitespace') -> tf.keras.layers.TextVectorization:
    vectorize_layer = tf.keras.layers.TextVectorization(
        max_tokens=max_features,
        split=split,
        output_mode=output_mode,
        output_sequence_length=max_len,
        pad_to_max_tokens=True)
    if train_ds is not None:
        text_ds = train_ds.map(lambda x, y: x)
        vectorize_layer.adapt(text_ds)
    else:
        assert (vocabulary is not None, "if train_ds is None, vocabulary can not be None")
        vectorize_layer.adapt(tf.data.Dataset.from_tensor_slices(["just for init weights"]))
        vectorize_layer.set_vocabulary(vocabulary)
    logging.info(f"Generate vectorize layer successfully, and adapt: {vectorize_layer.is_adapted}")
    return vectorize_layer


def get_bert_tokenizer(vocab):
    lookup_table = tf.lookup.StaticVocabularyTable(
        tf.lookup.KeyValueTensorInitializer(
            keys=vocab,
            key_dtype=tf.string,
            values=tf.range(tf.size(vocab, out_type=tf.int64), dtype=tf.int64),
            value_dtype=tf.int64),
        num_oov_buckets=1,
        lookup_key_dtype=tf.string
    )


def train_format_data(filename):
    pass
