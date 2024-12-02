import {
  Component,
  OnChanges,
  Input,
  SimpleChanges,
  SkipSelf,
} from '@angular/core';
import { DTOProduct } from '../../shared/dto/DTOProduct';
import { Router } from '@angular/router';
import { RatingService } from '../../shared/services/rating.service';

@Component({
  selector: 'box-product',
  templateUrl: './boxProduct.component.html',
  styleUrls: ['./boxProduct.component.scss'],
})
export class BoxProductComponent implements OnChanges {
  @Input() data: DTOProduct;
  salePrice: number = 0;
  saleConvert: string = '';
  selected = 0;
  hovered = 0;
  ratingValue: number = 0;
  readonly = true;
  inforProduct = 'infor-product';
  rating = 0;

  constructor(
    private route: Router,
    @SkipSelf() private ratingService: RatingService
  ) {}

  ngOnInit(): void {
    this.calculateSalePrice();
    this.convertToPercentage();
    this.updateRating(this.data.ProductID);
  }
  ngOnChanges(changes: SimpleChanges): void {
    if (changes['data'] && this['data']) {
      this.calculateSalePrice();
      this.convertToPercentage();
    }
  }
  private calculateSalePrice(): void {
    this.salePrice = this['data'].Sale
      ? this['data'].Price - this['data'].Price * this['data'].Sale
      : this['data'].Price;
  }

  private convertToPercentage(): string {
    this.saleConvert = (this['data'].Sale * 100).toString() + '%';
    return this.saleConvert;
  }

  updateRating(ProductID) {
    this.ratingService.getDataById(ProductID).subscribe((res) => {
      let total_ratings =
        res.Data._5star +
        res.Data._4star +
        res.Data._3star +
        res.Data._2star +
        res.Data._1star;
      let stars =
        5 * res.Data._5star +
        4 * res.Data._4star +
        3 * res.Data._3star +
        2 * res.Data._2star +
        1 * res.Data._1star;
      const average_rating = stars / total_ratings;
      this.rating = average_rating;
    });
  }

  navigateDetail() {
    this.route.navigate(['/product', this.data.Name]);
  }

  onRatingProduct(event: any) {
    console.log(event);
  }
}
