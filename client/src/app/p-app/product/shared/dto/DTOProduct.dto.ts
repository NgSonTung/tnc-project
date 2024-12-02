export class DTOProduct {
  Name: string;
  Sale: string;
  Image: string;
  Price: number;
  Stock: number;
  ProductID: number;
  Favorite: number;
  productID: number;
  CategoryID: number;
  Description: string;
  StatusID: number;
  CreatedAt: string;
  BrandName: string;
  Base64Image: string;
  constructor() {
    this.Name = '';
    this.Sale = '';
    this.Image = '';
    this.Price = 0;
    this.Stock = 0;
    this.ProductID = null;
    this.Favorite = 0;
    this.productID = null;
    this.CategoryID = null;
    this.Description = '';
    this.StatusID = 0;
    this.CreatedAt = null;
    this.BrandName = '';
    this.Base64Image = '';
  }
}
