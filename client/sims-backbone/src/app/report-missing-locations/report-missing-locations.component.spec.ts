import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ReportMissingLocationsComponent } from './report-missing-locations.component';
import { Component, Input } from '@angular/core';
import { Studies, ReportService } from '../typescript-angular-client';
import { createAuthServiceSpy, asyncData } from '../../testing/index.spec';
import { OAuthService } from 'angular-oauth2-oidc';
import { HttpClient } from '@angular/common/http';

@Component({ selector: 'app-studies-list', template: '' })
class StudiesListStubComponent {
  @Input() studies: Studies;
}

describe('ReportMissingLocationsComponent', () => {
  let component: ReportMissingLocationsComponent;
  let fixture: ComponentFixture<ReportMissingLocationsComponent>;

  let httpClientSpy: { get: jasmine.Spy };
  let reportService: ReportService;

  beforeEach(async(() => {

    let authService = createAuthServiceSpy();

    httpClientSpy = jasmine.createSpyObj('HttpClient', ['get']);

    httpClientSpy.get.and.returnValue(asyncData({ count: 0, locations: [] }));

    reportService = new ReportService(<any>httpClientSpy, '', authService.getConfiguration());

    TestBed.configureTestingModule({
      declarations: [
        ReportMissingLocationsComponent,
        StudiesListStubComponent
      ],
      providers: [
        { provide: OAuthService, useValue: authService },
        { provide: HttpClient, useValue: httpClientSpy },
        { provide: ReportService, useValue: reportService }
      ]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ReportMissingLocationsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
