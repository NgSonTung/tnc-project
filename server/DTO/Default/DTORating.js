module.exports = class DTORating {
  constructor(data) {
    this.RatingID = data.RatingID;
    this._5star = data._5star;
    this._4star = data._4star;
    this._3star = data._3star;
    this._2star = data._2star;
    this._1star = data._1star;
    this.ProductID = data.ProductID;
    if (!data.CreatedAt) data.CreatedAt = new Date().toISOString();
    this.CreatedAt = data.CreatedAt;
  }
};
