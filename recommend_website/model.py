import pandas as pd


class ChampionRecModel:

    def __init__(self, synergy_matrix, counter_matrix,  ally_champions=[], enemy_champions=[], position = []):
        self.synergy_matrix = synergy_matrix
        self.counter_matrix = counter_matrix
        self.ally_champions = ally_champions
        self.enemy_champions = enemy_champions
    
    def get_recommendation(self, position):
        # Extract just the champion names from ally_champions and enemy_champions
        ally_champion_names = [champ for champ, pos in self.ally_champions]
        enemy_champion_names = [champ for champ, pos in self.enemy_champions]

        # Calculate synergy scores for potential champions
        # Exclude already picked champions by the ally team and enemy team
        potential_champions = set(self.synergy_matrix[position].keys()) - set(ally_champion_names) - set(enemy_champion_names)
        
        synergy_scores = {}
        for champ in potential_champions:
            synergy_score = 0
            for ally, ally_pos in self.ally_champions:
                # Check if the ally champion is not the same as the potential champion
                if ally != champ:
                    synergy_score += self.synergy_matrix.get(ally_pos, {}).get(ally, {}).get(position, {}).get(champ, 0)
            synergy_scores[champ] = synergy_score

        # Calculate counter scores for potential champions
        counter_scores = {}
        for champ in potential_champions:
            counter_score = 0
            for enemy, enemy_pos in self.enemy_champions:
                counter_score += self.counter_matrix.get(position, {}).get(champ, {}).get(enemy_pos, {}).get(enemy, 0)
            counter_scores[champ] = counter_score

        # Combine scores and create a list of tuples
        combined_scores = [(champ, synergy_scores[champ], counter_scores[champ], synergy_scores[champ] + counter_scores[champ]) for champ in potential_champions]

        # Create a DataFrame
        df = pd.DataFrame(combined_scores, columns=['Champion', 'Synergy Score', 'Counter Score', 'Total Score'])
        df = df[df['Total Score'] != 0]

        # Calculate Harmonic Score
        df['Harmonic Score'] = 2 * (df['Synergy Score'] * df['Counter Score']) / df['Total Score']
        # Sort the DataFrame by the best overall score
        df_sorted = df.sort_values(by='Harmonic Score', ascending=False)
        df_sorted.drop(columns = ['Total Score'], inplace=True)
        
        # best_synergy = df_sorted[df_sorted['Synergy Score'] == max(df_sorted['Synergy Score'])]
        # best_counter = df_sorted[df_sorted['Counter Score'] == max(df_sorted['Counter Score'])]
        
        return df_sorted.reset_index(drop=True)