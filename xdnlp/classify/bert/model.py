import os
import time
import joblib
import tensorflow as tf
import tensorflow_hub as hub
import tensorflow_text as text
from xdnlp.bert import optimization


class BertClassify(tf.keras.Model):
    """A text Classify use Bert or Albert pre training
    handle_encoder: the encoder model dir, saved_model format,
                    can use the model in tensorflow hub or local
    handle_preprocess: the preprocess model dir,saved_model format,
                    can use the model in tensorflow hub or local
    """

    def __init__(self,
                 handle_encoder,
                 handle_preprocess,
                 classifer_activation=None,
                 categories=2):

        self.handle_preprocess = handle_preprocess
        self.handle_encoder = handle_encoder

        text_input = tf.keras.layers.Input(shape=(), dtype=tf.string, name='text')
        preprocessing_layer = hub.KerasLayer(handle_preprocess, name='preprocessing')
        encoder_inputs = preprocessing_layer(text_input)
        encoder = hub.KerasLayer(handle_encoder, trainable=True, name='BERT_encoder')
        outputs = encoder(encoder_inputs)
        net = outputs['pooled_output']
        net = tf.keras.layers.Dropout(0.1)(net)
        net = tf.keras.layers.Dense(categories, activation=classifer_activation, name='classifier')(net)
        super(BertClassify, self).__init__(inputs=text_input, outputs=net)

    def preview_train_data(self, train_ds):
        for text_batch, label_batch in train_ds.take(1):
            for i in range(3):
                print(f'Review: {text_batch.numpy()[i]}')
                label = label_batch.numpy()[i]
                print(f'Label : {label} ({self.class_names[label]})')

    def preview_preprocess_encoder(self, txt: str):

        preprocess_model = hub.KerasLayer(self.handle_preprocess)
        encoder_model = hub.KerasLayer(self.handle_encoder)

        text_test = [txt]
        text_preprocessed = preprocess_model(text_test)
        print(f'Text       : {txt}')
        print(f'Keys       : {list(text_preprocessed.keys())}')
        print(f'Shape      : {text_preprocessed["input_word_ids"].shape}')
        print(f'Word Ids   : {text_preprocessed["input_word_ids"][0, :12]}')
        print(f'Input Mask : {text_preprocessed["input_mask"][0, :12]}')
        print(f'Type Ids   : {text_preprocessed["input_type_ids"][0, :12]}')
        bert_results = encoder_model(text_preprocessed)
        print(f'Loaded BERT: {self.handle_encoder}')
        print(f'Pooled Outputs Shape:{bert_results["pooled_output"].shape}')
        print(f'Pooled Outputs Values:{bert_results["pooled_output"][0, :12]}')
        print(f'Sequence Outputs Shape:{bert_results["sequence_output"].shape}')
        print(f'Sequence Outputs Values:{bert_results["sequence_output"][0, :12]}')

    def preview_classify(self, model):
        text_test = ['this is such an amazing movie!']
        bert_raw_result = model(tf.constant(text_test))
        print(f'raw result: {tf.sigmoid(bert_raw_result)}')

    def load_data(self,
                  train_dir,
                  test_dir,
                  batch_size=32,
                  validation_split=0.2,
                  seed=42,
                  buffer_size=tf.data.AUTOTUNE):
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
        raw_train_ds = tf.keras.preprocessing.text_dataset_from_directory(
            train_dir,
            batch_size=batch_size,
            validation_split=validation_split,
            subset='training',
            seed=seed)
        self.class_names = raw_train_ds.class_names
        train_ds = raw_train_ds.cache().prefetch(buffer_size=buffer_size)

        val_ds = tf.keras.preprocessing.text_dataset_from_directory(
            train_dir,
            batch_size=batch_size,
            validation_split=validation_split,
            subset='validation',
            seed=seed)
        val_ds = val_ds.cache().prefetch(buffer_size=buffer_size)

        test_ds = tf.keras.preprocessing.text_dataset_from_directory(
            test_dir,
            batch_size=batch_size)
        test_ds = test_ds.cache().prefetch(buffer_size=buffer_size)

        return train_ds, val_ds, test_ds

    def train(self, train_ds, val_ds, epochs=5, init_lr=3e-5, callbacks=[], verbose=1):
        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
        steps_per_epoch = tf.data.experimental.cardinality(train_ds).numpy()
        num_train_steps = steps_per_epoch * epochs
        num_warmup_steps = int(0.1 * num_train_steps)
        optimizer = optimization.create_optimizer(init_lr=init_lr,
                                                  num_train_steps=num_train_steps,
                                                  num_warmup_steps=num_warmup_steps,
                                                  optimizer_type='adamw')
        save_path = os.path.join("models", str(int(time.time())))
        checkpoint_path = os.path.join(save_path, "cp-{epoch:04d}.ckpt")
        os.makedirs(save_path)
        joblib.dump(self.class_names, os.path.join(save_path, "label_name.pic"))
        if len(callbacks) == 0:
            cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                             save_weights_only=True,
                                                             verbose=verbose,
                                                             save_freq="epoch")
        callbacks = [cp_callback]

        self.compile(optimizer=optimizer,
                     loss=loss,
                     metrics=["accuracy"])

        self.fit(train_ds,
                 validation_data=val_ds,
                 epochs=epochs,
                 callbacks=callbacks,
                 verbose=verbose)


if __name__ == '__main__':
    # model = BertClassify("https://tfhub.dev/tensorflow/small_bert/bert_en_uncased_L-4_H-512_A-8/1",
    #                      "https://tfhub.dev/tensorflow/bert_en_uncased_preprocess/3",
    #                      categories=2)

    model = BertClassify("/home/geb/PycharmProjects/xdnlp/xdnlp/data/hub_models/albert_base_zh",
                         "/home/geb/PycharmProjects/xdnlp/xdnlp/data/hub_models/bert_zh_preprocess_3",
                         categories=2)

    train_ds, val_ds, test_ds = model.load_data("/home/geb/jonas/train", "/home/geb/jonas/test", )
    model.preview_train_data(train_ds)
    # model.preview_classify()
    model.train(train_ds, val_ds)

    loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)

    epochs = 5
    steps_per_epoch = tf.data.experimental.cardinality(model.train_ds).numpy()
    num_train_steps = steps_per_epoch * epochs
    num_warmup_steps = int(0.1 * num_train_steps)

    init_lr = 3e-5
    optimizer = optimization.create_optimizer(init_lr=init_lr,
                                              num_train_steps=num_train_steps,
                                              num_warmup_steps=num_warmup_steps,
                                              optimizer_type='adamw')

    model.compile(optimizer=optimizer,
                  loss=loss,
                  metrics=["accuracy"])

    history = model.fit(model.train_ds,
                        validation_data=model.val_ds,
                        epochs=epochs)
