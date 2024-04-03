import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { TournoiService } from "../services/tournoi.service";
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { RouterLink } from '@angular/router';

@Component({
  selector: 'app-tournoi',
  standalone: true,
  imports: [CommonModule, HttpClientModule, FormsModule, RouterLink],
  providers: [TournoiService],
  templateUrl: './tournoi.component.html',
})
export class TournoiComponent {
  items: any;
  showItems = true;

  nom: string = '';
  date: string = '';
  format: string = '';
  ageMin: number = 5;
  ageMax: number = 90;
  niveau: string = '';

/*
* {
    _id: '52',
    nomTournoi: 'Test',
    phase: 'Phase de poule',
    format: 'Simple',
    joueurs: [
      { _id: '2', nom: 'boudjemai', prenom: 'ali-akbar' },
      { _id: '96', nom: 'Ward', prenom: 'Riley' }
    ],
    scores: '0-0',
    idTable: '54',
    status: 'Prévu'
  }
* */
  constructor(private http: HttpClient, private serviceTournoi: TournoiService, private router: Router) {
    this.getItems();
  }

  getItems() {
    this.serviceTournoi.getTournois().subscribe(
      data => {
        this.items = data;
      },
      erreur => {
        console.error('erreur!', erreur);
      }
    );
  }

  afficherDetailTournoi(id: string) {
    this.router.navigate(['/modifier-tournoi', id]);
  }

  afficherTournois() {
    this.showItems = !this.showItems;
  }

  envoieForm() {
    const tournoiData = {
      nom: this.nom,
      date: this.date,
      format: this.format,
      ageMin: this.ageMin,
      ageMax: this.ageMax,
      niveau: this.niveau
    };

    this.serviceTournoi.insererTournoi(tournoiData).subscribe(
      response => {
        console.log('Tournoi inséré avec succès:', response);
      },
      error => {
        console.error('Erreur lors de l\'insertion du tournoi:', error);
      }
    );
  }
}
