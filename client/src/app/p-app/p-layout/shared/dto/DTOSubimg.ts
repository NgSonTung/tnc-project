export class DTOSubimg {
  SubimgID: number;
  image: string;
  Alt: string;
  ProductID: number;
  createdAt: string;

  constructor(
    subimgID: number,
    image: string,
    alt: string,
    productID: number,
    createdAt: string
  ) {
    this.SubimgID = subimgID;
    this.image = image;
    this.Alt = alt;
    this.ProductID = productID;
    this.createdAt = createdAt;
  }
}
