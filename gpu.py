import tensorflow as tf
hello=tf.constant("hello,world")
sess=tf.Session()
print(sess.run(hello))