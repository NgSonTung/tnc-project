import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { DTOOrder } from '../dto/DTOOrder';
import { DTOResponse } from '../dto/DTOResponse';
import { DTOOrderDetailPayload } from '../dto/DTOOrderDetailPayload.';
import { environment } from 'src/app/environments/environments';

@Injectable({
  providedIn: 'root',
})
export class OrderService {
  constructor(private http: HttpClient) {
    console.log('order service started');
  }

  getData(
    page: number,
    pageSize: number,
    filterStr: string = ''
  ): Observable<DTOResponse> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());
    return this.http
      .get<DTOResponse>(`/api/v1/order/product/${filterStr}`, {
        params,
      })
      .pipe(catchError(this.handleError));
  }

  getOrderDetail(orderID: number, userID: number): Observable<DTOResponse> {
    const headers = new HttpHeaders({
      OrderID: orderID,
      UserID: userID,
    });
    return this.http
      .get<DTOResponse>(`${environment.apiUrl}/order/orderdetails`, { headers })
      .pipe(catchError(this.handleError));
  }

  getDataById(id: number): Observable<DTOResponse> {
    return this.http
      .get<DTOResponse>(`${environment.apiUrl}/order/user/${id}`)
      .pipe(catchError(this.handleError));
  }

  createData(order: DTOOrder): Observable<DTOResponse> {
    return this.http
      .post<DTOResponse>('/api/v1/order', order)
      .pipe(catchError(this.handleError));
  }

  updateData(order: any): Observable<DTOResponse> {
    return this.http
      .patch<DTOResponse>(`/api/v1/order/product`, order)
      .pipe(catchError(this.handleError));
  }

  addToCart(order: any): Observable<DTOResponse> {
    return this.http
      .post<DTOResponse>(`/api/v1/order/product`, order)
      .pipe(catchError(this.handleError));
  }

  updateCart(order: any): Observable<DTOResponse> {
    return this.http
      .patch<DTOResponse>(`/api/v1/order/product`, order)
      .pipe(catchError(this.handleError));
  }

  deleteDataById(id: number): Observable<DTOResponse> {
    return this.http
      .delete<DTOResponse>(`/api/v1/order/${id}`)
      .pipe(catchError(this.handleError));
  }

  cancelOrder(id: number): Observable<DTOResponse> {
    return this.http
      .patch<DTOResponse>(`/api/v1/order/cancelorder/${id}`, {})
      .pipe(catchError(this.handleError));
  }

  private handleError(error: any) {
    console.error('An error occurred:', error);
    return throwError(
      () => new Error('Something went wrong. Please try again later.')
    );
  }
}
