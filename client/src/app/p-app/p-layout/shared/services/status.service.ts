import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { DTOPayment } from '../dto/DTOPayment';
import { DTOStatus } from '../dto/DTOStatus';

@Injectable({
  providedIn: 'root',
})
export class PaymentService {
  constructor(private http: HttpClient) {
    console.log('status service started');
  }

  getData(
    page: number,
    pageSize: number,
    filterStr: string
  ): Observable<DTOStatus> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('pageSize', pageSize.toString());
    return this.http
      .get<DTOStatus>(`/api/v1/status/${filterStr}`, {
        params,
      })
      .pipe(catchError(this.handleError));
  }

  getDataById(id: number): Observable<DTOStatus> {
    return this.http
      .get<DTOStatus>(`/api/v1/status/${id}`)
      .pipe(catchError(this.handleError));
  }

  createData(status: DTOPayment): Observable<DTOStatus> {
    return this.http
      .post<DTOStatus>('/api/v1/status', status)
      .pipe(catchError(this.handleError));
  }

  updateData(id: number, status: DTOPayment): Observable<DTOStatus> {
    return this.http
      .patch<DTOStatus>(`/api/v1/status/${id}`, status)
      .pipe(catchError(this.handleError));
  }

  deleteDataById(id: number): Observable<DTOStatus> {
    return this.http
      .delete<DTOStatus>(`/api/v1/status/${id}`)
      .pipe(catchError(this.handleError));
  }

  private handleError(error: any) {
    console.error('An error occurred:', error);
    return throwError(
      () => new Error('Something went wrong. Please try again later.')
    );
  }
}
