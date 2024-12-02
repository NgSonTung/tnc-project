export class DTORating {
  RatingID: number;
  _5star: number;
  _4star: number;
  _3star: number;
  _2star: number;
  _1star: number;
  ProductID: number;
  CreatedAt: string;

  constructor(
    ratingID: number,
    _5star: number,
    _4star: number,
    _3star: number,
    _2star: number,
    _1star: number,
    productID: number,
    createdAt: string
  ) {
    this.RatingID = ratingID;
    this._5star = _5star;
    this._4star = _4star;
    this._3star = _3star;
    this._2star = _2star;
    this._1star = _1star;
    this.ProductID = productID;
    this.CreatedAt = createdAt;
  }
}
