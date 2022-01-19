import tensorflow as tf
import numpy as np
import os
import datetime
from tensorflow import keras
import joblib

class TextCNN(tf.keras.Model):

    def __init__(self, input_shape: tuple,
                 class_names: list,
                 vectorize_layer: keras.layers.TextVectorization,
                 model_dir: str = "models",
                 embedding_size: int = 128,
                 hidden_size: int = 256,
                 filter_sizes: list = [3, 4, 5],
                 num_filters: int = 256,
                 dropout: float = 0.2,
                 embedding_matrix_file: str = None,
                 embedding_matrix_trainable: bool = True,
                 is_train=True):
        embedding_matrix = np.load(embedding_matrix_file) if embedding_matrix_file is not None else None
        vocab_size = vectorize_layer.vocabulary_size()
        inputs = keras.Input(shape=(), dtype=tf.string, name='text')
        inputs_vec = vectorize_layer(inputs)
        if embedding_matrix is not None:
            x = keras.layers.Embedding(vocab_size,
                                       embedding_size,
                                       embeddings_initializer=tf.keras.initializers.Constant(self.embedding_matrix),
                                       trainable=embedding_matrix_trainable)(inputs_vec)
        else:
            x = keras.layers.Embedding(vocab_size, embedding_size)(inputs_vec)
        xs = [
            keras.layers.Conv1D(num_filters, filter_size, activation='relu', input_shape=input_shape, padding='same',
                                name=f"cnn_size_{filter_size}")(x)
            for filter_size in filter_sizes]
        xs = [keras.layers.MaxPool1D(pool_size=input_shape[0], name=f"max_pool_{i}")(x) for i, x in enumerate(xs)]
        x = keras.layers.Concatenate(axis=-1, name="concatenate")(xs)
        x = keras.layers.Flatten()(x)
        x = keras.layers.Dropout(dropout)(x)
        x = keras.layers.Dense(hidden_size, activation='relu', name="hidden_layer")(x)
        x = keras.layers.Dense(len(class_names), activation='softmax', name="output")(x)
        super(TextCNN, self).__init__(inputs=inputs, outputs=x, name="text_cnn")
        # save model config
        if is_train:
            self.model_dir = os.path.join(model_dir, datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
            if not os.path.exists(self.model_dir):
                os.makedirs(self.model_dir)
            joblib.dump(dict(class_names=list(class_names),
                             max_features=vocab_size,
                             max_len=input_shape[0],
                             embedding_size=embedding_size,
                             hidden_size=hidden_size,
                             filter_sizes=filter_sizes,
                             num_filters=num_filters,
                             dropout=dropout,
                             vocabulary=list(vectorize_layer.get_vocabulary())),
                        os.path.join(self.model_dir, "model_config.pkl"))
        self.summary()

    @classmethod
    def get_model_config(cls, path):
        return joblib.load(os.path.join(path, "model_config.pkl"))

    def train(self, train_ds, val_ds, epochs=20, save_weights_only=True):
        checkpoint_path = os.path.join(self.model_dir, "cp-{epoch:04d}.ckpt")
        cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                         save_weights_only=save_weights_only,
                                                         verbose=1,
                                                         save_freq="epoch")
        log_dir = os.path.join(self.model_dir, "logs/")
        tensorboard_callback = tf.keras.callbacks.TensorBoard(log_dir=log_dir)

        self.compile(optimizer='adam',
                     loss='categorical_crossentropy',
                     metrics=['accuracy'])

        self.fit(train_ds,
                 validation_data=val_ds,
                 epochs=epochs,
                 callbacks=[cp_callback, tensorboard_callback])

        self.save(os.path.join(self.model_dir, "my_model"))
