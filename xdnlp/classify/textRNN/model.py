from re import I
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras import layers
import numpy as np
import os
import time
import joblib


class TextRNN(tf.keras.Model):

    def __init__(self,
                 vectorize_layer: layers.TextVectorization,
                 class_names: list,
                 model_dir: str = "models_TextRNN",
                 embedding_size: int = 128,
                 rnn_hidden_size: int = 256,
                 fc_hidden_size: int = 128,
                 num_layers: int = 2,
                 dropout: float = 0.2,
                 embedding_matrix_file: str = None,
                 embedding_matrix_trainable: bool = True,
                 save_model_config=True):
        embedding_matrix = np.load(embedding_matrix_file) if embedding_matrix_file is not None else None
        vocab_size = vectorize_layer.vocabulary_size()
        self.model_dir = os.path.join(model_dir, time.strftime(("%Y%m%d-%H%M%S"), time.localtime()))
        inputs = layers.Input(shape=(), dtype=tf.string, name='text')
        inputs_vec = vectorize_layer(inputs)
        if embedding_matrix is not None:
            x = layers.Embedding(vocab_size,
                                 embedding_size,
                                 embeddings_initializer=keras.initializers.Constant(self.embedding_matrix),
                                 trainable=embedding_matrix_trainable)(inputs_vec)
        else:
            x = layers.Embedding(vocab_size, embedding_size)(inputs_vec)

        for i in range(num_layers):
            x = layers.Bidirectional(layers.LSTM(rnn_hidden_size, return_sequences=True),
                                     name="BiLSTM_layer_%d" % (i))(x)
        x = RNN_Attention(name="attention_layer")(x)
        x = layers.Flatten()(x)
        x = layers.Dropout(dropout)(x)
        x = layers.Dense(fc_hidden_size, activation='relu', name="dense_layer_0")(x)
        outputs = layers.Dense(len(class_names), activation='softmax', name="dense_layer_1")(x)
        super(TextRNN, self).__init__(inputs=inputs, outputs=outputs, name="text_rnn")

        # save model config
        if save_model_config:
            if not os.path.exists(self.model_dir):
                os.makedirs(self.model_dir)
            joblib.dump(dict(class_names=list(class_names),
                             max_features=vocab_size,
                             max_len=inputs_vec.shape[1],
                             embedding_size=embedding_size,
                             rnn_hidden_size=rnn_hidden_size,
                             fc_hidden_size=fc_hidden_size,
                             num_layers=num_layers,
                             dropout=dropout,
                             vocabulary=list(vectorize_layer.get_vocabulary())),
                        os.path.join(self.model_dir, "model_config.pkl"))
        self.summary()

    @classmethod
    def get_model_config(cls, path):
        return joblib.load(os.path.join(path))

    def train(self, train_ds, val_ds, epochs=20, save_weights_only=True):
        checkpoint_path = os.path.join(self.model_dir, "checkpoint", "cp-{epoch:04d}.ckpt")
        cp_callback = keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                      save_weights_only=save_weights_only,
                                                      verbose=1,
                                                      save_freq="epoch")
        log_dir = os.path.join(self.model_dir, "logs")
        tensorboard_callback = keras.callbacks.TensorBoard(log_dir=log_dir,
                                                           update_freq=1000,
                                                           write_graph=False)

        self.compile(optimizer='adam',
                     loss='categorical_crossentropy',
                     metrics=['accuracy'])

        self.fit(train_ds,
                 validation_data=val_ds,
                 epochs=epochs,
                 callbacks=[cp_callback, tensorboard_callback])

        self.save(os.path.join(self.model_dir, "my_model"))


class RNN_Attention(layers.Layer):
    def __init__(self, **kwargs):
        super(RNN_Attention, self).__init__(**kwargs)
        self.attention = layers.Attention()

    def build(self, input_shape):
        self.w = self.add_weight(shape=(1, input_shape[-1]),
                                 initializer="random_normal",
                                 trainable=True,
                                 name="attention_query")

    def call(self, inputs):
        outputs = self.attention([self.w, inputs])
        return outputs