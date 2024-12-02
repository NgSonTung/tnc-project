import { Injectable, OnInit, SkipSelf } from '@angular/core';
import { Observable, of, BehaviorSubject } from 'rxjs';
import { HttpHeaders, HttpParams } from '@angular/common/http';
import { HttpClient } from '@angular/common/http';
import { DTOResponse } from 'src/app/p-app/p-layout/shared/dto/DTOResponse';
import { CategoryService } from 'src/app/p-app/p-layout/shared/services/category.service';
import { Subject, Subscription, takeUntil } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class ProductAPIService {
  ngUnsubscribe = new Subject<void>();

  productURL = '/api/v1/product/';
  testDetailProduct = 'https://api.npoint.io/09883bf2746395a86b36';
  arrlabelFilter: BehaviorSubject<any[]> = new BehaviorSubject<any[]>([]);
  removeItem: BehaviorSubject<string[]> = new BehaviorSubject<string[]>([]);
  queryFilter: BehaviorSubject<string> = new BehaviorSubject<string>('');
  constructor(private http: HttpClient) {}

  getArrlabelFilter(): Observable<any[]> {
    return this.arrlabelFilter.asObservable();
  }

  setArrlabelFilter(arr: any[]) {
    this.arrlabelFilter.next(arr);
  }

  getRemoveItem(): Observable<string[]> {
    return this.removeItem.asObservable();
  }

  setRemoveItem(arr: string[]) {
    if (arr.length > 0) {
      const currentQuery = this.queryFilter.value;

      const arrQuery = currentQuery.split(',').filter(Boolean);

      const updatedQueryArray = arrQuery.filter(
        (item) => !item.includes(`:${arr[0]}`)
      );

      const updatedQuery = updatedQueryArray
        .map((item, index) => {
          return item + ',';
        })
        .join('');
      console.log('updatedQuery', updatedQuery);
      this.queryFilter.next(updatedQuery);
      console.log('this.queryFilter.value', this.queryFilter.value);
    }
    this.removeItem.next(arr);
  }

  getQueryFilter(): Observable<string> {
    return this.queryFilter.asObservable();
  }

  setQueryFilter(query: string) {
    const currentQuery = this.queryFilter.value;

    const updatedQuery = currentQuery ? `${currentQuery}${query}` : query;

    this.queryFilter.next(updatedQuery);
  }

  GetProducts(queryString: string) {
    return new Observable<any>((obs) => {
      this.http.get<any>(`${this.productURL}${queryString}`).subscribe(
        (res) => {
          obs.next(res);
          obs.complete();
        },
        (err) => {
          obs.error(err);
          obs.complete();
        }
      );
    });
  }

  GetProductDetail() {
    return new Observable<DTOResponse>((obs) => {
      this.http.get<any>(this.testDetailProduct).subscribe(
        (res) => {
          obs.next(res);
          obs.complete();
        },
        (err) => {
          obs.error(err);
          obs.complete();
        }
      );
    });
  }
}
