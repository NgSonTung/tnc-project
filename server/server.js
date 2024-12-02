const dotenv = require("dotenv");
dotenv.config({
  path: "./config.env",
});

const app = require("./app");

const sql = require("mssql");
const dbConfig = require("./database/dbconfig");

app.set("view engine", "hbs");
app.get("/", (req, res) => {
  res.render("sucess_payment");
});
//https://www.npmjs.com/package/mssql#asyncawait => Global Pool Single Instance
const appPool = new sql.ConnectionPool(dbConfig.sqlConfig);
appPool
  .connect()
  .then(function (pool) {
    dbConfig.db.pool = pool;
    console.log("SQL Connected!");
  })
  .catch(function (err) {
    console.error("Error creating connection pool", err);
  });
//START SERVER
const PORT = process.env.PORT;
app.listen(PORT, () => {
  console.log(`App running on port ${PORT}...`);
});
