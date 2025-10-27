//импорт пакетов
const express = require('express');
//определение экземпляра и порта
const app = express();
const PORT = process.env.PORT || 4000;
//маршрут по умолчанию
app.get('/', (req, res) => {
    res.status(200);
    res.send('Hello World!');
});
//запуск сприложения
app.listen(PORT, () => {
    console.log(`App listening on port ${PORT}`);
});


