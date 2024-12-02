import { Injectable } from '@angular/core';
import { Observable, shareReplay } from 'rxjs';
import { HttpHeaders } from '@angular/common/http';
import { HttpClient } from '@angular/common/http';
import { DTOResponse } from '../dto/DTOResponse';

@Injectable({
  providedIn: 'root',
})
export class LayoutAPIService {
  constructor(private http: HttpClient) {}
  brandURL = '/api/v1/brand';
  categoryURL = '/api/v1/category/';
  productURL = '/api/v1/product/';
  filterProductURL = '/api/v1/product';
  //Chưa chỉnh lại res từ api nên chưa gán DTO được

  GetProducts() {
    return new Observable<any>((obs) => {
      this.http.get<any>(this.productURL).subscribe(
        (res) => {
          obs.next(res);
        },
        (err) => {
          obs.error(err);
        }
      );
    });
  }

  GetFilterProducts(filterProductURL: string, headers: any) {
    return new Observable<any>((obs) => {
      this.http.get<any>(filterProductURL, { headers: headers }).subscribe(
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

  GetBrands() {
    return new Observable<DTOResponse>((obs) => {
      this.http.get<DTOResponse>(this.brandURL).subscribe(
        (res) => {
          3;
        },
        (err) => {
          obs.error(err);
          obs.complete();
        }
      );
    });
  }

  GetCategories() {
    return new Observable<DTOResponse>((obs) => {
      this.http.get<DTOResponse>(this.categoryURL).subscribe(
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
