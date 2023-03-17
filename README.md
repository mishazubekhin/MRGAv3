<h1 align="center">MakeRussiaGreatAgain bot</h1>

### Not for copying and usage
by Zubekhin M.V.
# About
`ru` Ботинок создан для предоставления доступной демократии гражданам Россйиской Федерации путем освещения насущных проблем граждан всеобщим голосованием.
Голосование подкрепляется фотоматериалами, которые проходят через фильтр релевантности, самосозданной моделью Tensorflow.
Также создан фильтр на опредление непристойных слов и запрщение их.
Граждане для более объективного принятия какого либо решения выбирают свой регион проживания.
Дальнейшая судьба голосования в настоящий момент находится в процессе разработки. Необходимо получить АПИ органов власти для направления наиболее актальных и популярных голосваний.

`eng` Boot was created to provide affordable democracy to the citizens of the Russian Federation by highlighting the pressing problems of citizens by universal suffrage.
Voting is backed up by photo submissions that pass through a relevancy filter, a self-created Tensorflow model.
A filter has also been created to detect obscene words and prohibit them.
Citizens choose their region of residence for a more objective decision-making.
The further fate of voting is currently under development. It is necessary to obtain the API of the authorities in order to direct the most relevant and popular votes.

### Usage library
`Pyrogram`, `Request` for parsing photo for dataScience, `TensorFlow` for dataScience, `SQLite` database


## Link for use
https://t.me/MakeRussiaGreatAgain_bot

## Example
<p align="center">
<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExMWEzMzQzYjliMzA1NjE5YjYyNzcyNjE5ODZkNjJjZTIzMDViZDFmYiZjdD1n/ulRkl7gKquDbt1qHOo/giphy.gif">
</p>

<p align="center">
<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExODEwNDBjMDc2OTQxOGI0NDQzMGZjZTU2MGFlYTZmMDVkMGExMzBjMyZjdD1n/BRYrTZgeLGJv4XJdfN/giphy.gif">
</p>

<p align="center">
<img src="https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExODU4ODE0OGY1NzcwM2YwN2NjZmMyMzBlMmVmMzVlYmU3ODlhMzYzOCZjdD1n/FSksDdPNdzbHlQhGRY/giphy.gif">
</p>

## My model detect photo

`model = tf.keras.Sequential([base_layers,
    layers.Input((224, 224, 3)),
    layers.Conv2D(32, 3, activation='relu', padding='same'),
    layers.MaxPooling2D(),
    layers.Conv2D(32, 3, activation='relu', padding='same'),
    layers.MaxPooling2D(),
    layers.Flatten(),
    layers.Dense(20, activation=tf.nn.relu),  # input shape required
    layers.Dense(20, activation=tf.nn.relu),
    layers.Dense(20, activation=tf.nn.relu),
    layers.Dense(20, activation=tf.nn.relu),
    layers.Dense(1, activation='sigmoid')])`

`model.compile(
    optimizer=tf.keras.optimizers.Adam(),
    loss='binary_crossentropy',
    metrics=['accuracy']`

## `I wanna works in Tinkoff :)`