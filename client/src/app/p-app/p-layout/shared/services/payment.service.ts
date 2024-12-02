import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { DTOPayment } from '../dto/DTOPayment';
import { DTOResponse } from '../dto/DTOResponse';

@Injectable({
  providedIn: 'root',
})
export class PaymentService {
  constructor(private http: HttpClient) {
    console.log('payment service started');
  }

  getData(
    page: number,
    pageSize: number,
    filterStr: string
  ): Observable<DTOResponse> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());
    return this.http
      .get<DTOResponse>(`/api/v1/payment/${filterStr}`, {
        params,
      })
      .pipe(catchError(this.handleError));
  }

  getDataById(id: number): Observable<DTOResponse> {
    return this.http
      .get<DTOResponse>(`/api/v1/payment/${id}`)
      .pipe(catchError(this.handleError));
  }

  createData(payment: DTOPayment): Observable<DTOResponse> {
    return this.http
      .post<DTOResponse>('/api/v1/payment', payment)
      .pipe(catchError(this.handleError));
  }

  updateData(id: number, payment: DTOPayment): Observable<DTOResponse> {
    return this.http
      .patch<DTOResponse>(`/api/v1/payment/${id}`, payment)
      .pipe(catchError(this.handleError));
  }

  deleteDataById(id: number): Observable<DTOResponse> {
    return this.http
      .delete<DTOResponse>(`/api/v1/payment/${id}`)
      .pipe(catchError(this.handleError));
  }

  checkOut(body): Observable<any> {
    return this.http.post<any>(`/api/v1/payment/handlerPayment`, body);
  }

  private handleError(error: any) {
    console.error('An error occurred:', error);
    return throwError(
      () => new Error('Something went wrong. Please try again later.')
    );
  }
}
