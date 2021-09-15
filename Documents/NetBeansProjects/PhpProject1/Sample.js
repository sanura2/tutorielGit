//global setup: load the package

let express = require('express');
let ejs = require('ejs');

let app = express();


app.set('view engine', 'html');
app.engine('html', ejs.renderFile);


app.get('/route1', function (req, res) {
    res.setHeader("Content-Type", "text/html");
    res.send('Route 1 requested');
});

app.get('/route2', function (req, res) {

    res.setHeader("Content-Type", "text/html");
    res.send('Route 2 requested');
});

//set up the route for the max value: one for the form and one for the result
//route will call the page engine for the filling template

app.get('/frm3numbers', function (req, res) {
    res.setHeader('Content-Type', 'text/html');
    res.render('frm3numbers.html', {});
}
);

app.get('/rsMax', function (req, res) {
    n1 = parseInt(req.query.txt_number1); //name used in the html form
    n2 = parseInt(req.query.txt_number2);
    n3 = parseInt(req.query.txt_number3);

    if (n1 > n2) {
        max = n1;
    } else {
        max = n2;
    }
    if (n3 > max) {
        max = n3;
    }


    res.setHeader("Content-Type", "text/html");
    res.render('showMaxValue.html', {vMax: max});
});

app.listen(3001);