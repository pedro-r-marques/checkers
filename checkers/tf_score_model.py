import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers


class TransformerBlock(layers.Layer):
    def __init__(self, embed_dim, num_heads, ff_dim, rate=0.1):
        super(TransformerBlock, self).__init__()
        self.att = layers.MultiHeadAttention(
            num_heads=num_heads, key_dim=embed_dim)
        self.ffn = keras.Sequential(
            [layers.Dense(ff_dim, activation="relu"),
             layers.Dense(embed_dim), ]
        )
        self.layernorm1 = layers.LayerNormalization(epsilon=1e-6)
        self.layernorm2 = layers.LayerNormalization(epsilon=1e-6)
        self.dropout1 = layers.Dropout(rate)
        self.dropout2 = layers.Dropout(rate)

    def call(self, inputs, training):
        attn_output = self.att(inputs, inputs)
        attn_output = self.dropout1(attn_output, training=training)
        out1 = self.layernorm1(inputs + attn_output)
        ffn_output = self.ffn(out1)
        ffn_output = self.dropout2(ffn_output, training=training)
        return self.layernorm2(out1 + ffn_output)


class PositionEmbeddings(layers.Layer):
    def __init__(self):
        super(PositionEmbeddings, self).__init__()
        self.pos_vectors = self.add_weight(
            shape=(32, 12), name="pos_embeddings")

    def call(self, x):
        batch_size = tf.shape(x)[0]
        v = tf.broadcast_to(self.pos_vectors, [
                            batch_size] + list(self.pos_vectors.shape))
        return tf.concat([x, v], axis=-1)


def make_model_v0_1():
    board = layers.Input(shape=(8, 4, 4), dtype=tf.float32)
    player = layers.Input(shape=(2,), dtype=tf.float32)

    board_flat = layers.Reshape((32, 4))(board)
    b_vectors = PositionEmbeddings()(board_flat)

    t1 = TransformerBlock(16, 4, 32)(b_vectors)
    t2 = TransformerBlock(16, 4, 32)(t1)

    t_out = layers.Dense(8, activation='linear')(t2)
    t_flat = layers.Flatten()(t_out)
    t_vector = layers.Dense(48, name='t_vector')(t_flat)

    emb_vector = layers.Concatenate()([player, t_vector])

    h1 = layers.Dense(32)(emb_vector)
    out = layers.Dense(3, activation='sigmoid', name='output')(h1)

    model = keras.Model([board, player], out)
    model.compile('adam', loss='mse')
    return model
