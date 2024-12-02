import { Component, OnDestroy, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { Observable, filter, pluck, switchMap, tap } from 'rxjs';
import { LayoutAPIService } from '../p-layout/shared/services/layout-api.service';
import { ProductAPIService } from './shared/services/product-api.service';

@Component({
  selector: 'app-p-product',
  templateUrl: './product.component.html',
  styleUrls: ['./product.component.scss'],
})
export class ProductComponent implements OnInit, OnDestroy {
  categoryName: string = '';
  categoryName$: Observable<string>;

  testQueryString = "?page=1&pageSize=10&categoryID=3"

  constructor(private route: ActivatedRoute, private productAPIService: ProductAPIService) { }

  ngOnInit(): void {
    this.getURLParam()
  }

  getURLParam() {
    this.route.params.pipe(
      pluck('categoryname'),
      tap(value => this.categoryName = value
      ),
      switchMap(slug => {
        return this.productAPIService.GetProducts(this.testQueryString);
      }),
      filter(categoryName => !!categoryName)
    ).subscribe(val => console.log(val))
  }

  ngOnDestroy(): void {

  }
}
