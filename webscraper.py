"""
Apify Google Maps Reviews Scraper for Manhattan Restaurants
Uses multiple Apify accounts to maximize free tier usage
Collects 2,000+ reviews across different neighborhoods for bias analysis

Updated with:
- Validated field names from Apify compass/google-maps-reviews-scraper
- Robust error handling with retries
- Proper logging and progress tracking
"""

from apify_client import ApifyClient
from apify_client.exceptions import ApifyApiError
import pandas as pd
import json
import time
from typing import List, Dict, Optional
import random
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class ApifyMultiAccountScraper:
    """
    Manages multiple Apify API tokens to maximize free tier credits
    Each free account gets $5 credit = ~10,000 reviews at $0.50 per 1,000
    With 4 accounts, you can scrape 40,000+ reviews for free
    """
    
    # Validated field names from Apify compass/google-maps-reviews-scraper output
    FIELD_MAPPINGS = {
        'name': 'name',  # Reviewer name
        'stars': 'stars',  # Rating (1-5)
        'text': 'text',  # Review text
        'textTranslated': 'textTranslated',  # Translated text if available
        'publishedAtDate': 'publishedAtDate',  # Published date string
        'publishAt': 'publishAt',  # Timestamp
        'likesCount': 'likesCount',  # Number of likes
        'reviewerNumberOfReviews': 'reviewerNumberOfReviews',  # Total reviews by reviewer
        'responseFromOwnerText': 'responseFromOwnerText',  # Owner response
        'reviewId': 'reviewId',  # Unique review ID
        'reviewUrl': 'reviewUrl',  # Direct URL to review
        'isLocalGuide': 'isLocalGuide',  # Boolean for local guide status
    }
    
    def __init__(self, api_tokens: List[str], max_retries: int = 3):
        """
        Initialize with multiple API tokens
        
        Args:
            api_tokens: List of Apify API tokens from different accounts
            max_retries: Maximum number of retries for failed requests
        """
        if not api_tokens or len(api_tokens) == 0:
            raise ValueError("At least one API token is required")
            
        self.api_tokens = api_tokens
        self.current_token_index = 0
        self.clients = [ApifyClient(token) for token in api_tokens]
        self.all_reviews = []
        self.max_retries = max_retries
        
        logger.info(f"Initialized with {len(api_tokens)} Apify accounts")
        logger.info(f"Estimated capacity: ~{len(api_tokens) * 10000} reviews")
        logger.info(f"Max retries per request: {max_retries}")
    
    def get_next_client(self) -> ApifyClient:
        """
        Round-robin through API tokens to distribute usage
        """
        client = self.clients[self.current_token_index]
        token_index = self.current_token_index
        self.current_token_index = (self.current_token_index + 1) % len(self.clients)
        return client, token_index
    
    def _safe_get_field(self, item: Dict, field: str, default=None):
        """
        Safely extract field from item dict with fallback to None
        """
        return item.get(field, default)
    
    def scrape_restaurant_reviews(
        self,
        place_url: str,
        restaurant_name: str,
        neighborhood: str,
        cuisine_type: str = "Unknown",
        max_reviews: int = 100,
        sort_by: str = "newest"
    ) -> List[Dict]:
        """
        Scrape reviews from a single restaurant using Apify with retry logic
        
        Args:
            place_url: Google Maps URL of the restaurant
            restaurant_name: Name of the restaurant
            neighborhood: Neighborhood (Upper East Side, Hell's Kitchen, etc.)
            cuisine_type: Type of cuisine
            max_reviews: Maximum number of reviews to scrape
            sort_by: "newest", "mostRelevant", "highestRanking", "lowestRanking"
        
        Returns:
            List of review dictionaries
        """
        logger.info("=" * 60)
        logger.info(f"Scraping: {restaurant_name} ({neighborhood})")
        logger.info("=" * 60)
        
        # Configure the scraper input
        # Using compass/google-maps-reviews-scraper (official actor)
        run_input = {
            "startUrls": [{"url": place_url}],
            "maxReviews": max_reviews,
            "reviewsSort": sort_by,
            "language": "en",
            "personalData": False,  # Don't scrape personal reviewer data
            "maxImages": 0,  # Don't need images for text analysis
        }
        
        # Retry logic
        for attempt in range(self.max_retries):
            try:
                # Get next available client
                client, token_index = self.get_next_client()
                logger.info(f"Attempt {attempt + 1}/{self.max_retries} using account #{token_index + 1}")
                
                # Run the Actor and wait for completion
                run = client.actor("compass/google-maps-reviews-scraper").call(run_input=run_input)
                
                if not run or 'defaultDatasetId' not in run:
                    logger.error("Invalid response from Apify actor")
                    if attempt < self.max_retries - 1:
                        logger.info(f"Retrying in {2 ** attempt} seconds...")
                        time.sleep(2 ** attempt)
                        continue
                    else:
                        logger.error(f"Failed after {self.max_retries} attempts")
                        return []
                
                logger.info(f"Scraper completed. Dataset ID: {run['defaultDatasetId']}")
                
                # Fetch results from dataset
                reviews_data = []
                dataset_client = client.dataset(run['defaultDatasetId'])
                
                item_count = 0
                for item in dataset_client.iterate_items():
                    item_count += 1
                    
                    # Extract and structure the review data with safe field access
                    review = {
                        'restaurant_name': restaurant_name,
                        'neighborhood': neighborhood,
                        'cuisine_type': cuisine_type,
                        'place_url': place_url,
                        'reviewer_name': self._safe_get_field(item, 'name', 'Anonymous'),
                        'rating': self._safe_get_field(item, 'stars'),
                        'review_text': self._safe_get_field(item, 'text', ''),
                        'review_text_translated': self._safe_get_field(item, 'textTranslated', ''),
                        'review_length': len(self._safe_get_field(item, 'text', '')),
                        'published_date': self._safe_get_field(item, 'publishedAtDate', 'Unknown'),
                        'published_timestamp': self._safe_get_field(item, 'publishAt'),
                        'likes_count': self._safe_get_field(item, 'likesCount', 0),
                        'reviewer_total_reviews': self._safe_get_field(item, 'reviewerNumberOfReviews', 0),
                        'is_local_guide': self._safe_get_field(item, 'isLocalGuide', False),
                        'owner_response': self._safe_get_field(item, 'responseFromOwnerText'),
                        'review_id': self._safe_get_field(item, 'reviewId'),
                        'review_url': self._safe_get_field(item, 'reviewUrl'),
                    }
                    reviews_data.append(review)
                
                logger.info(f"Successfully extracted {len(reviews_data)} reviews from {restaurant_name}")
                self.all_reviews.extend(reviews_data)
                
                return reviews_data
                
            except ApifyApiError as e:
                logger.error(f"Apify API error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed after {self.max_retries} attempts for {restaurant_name}")
                    return []
                    
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"Failed after {self.max_retries} attempts for {restaurant_name}")
                    return []
        
        return []
    
    def scrape_multiple_restaurants(
        self,
        restaurants: List[Dict],
        reviews_per_restaurant: int = 100,
        delay_between_requests: tuple = (3, 7),
        save_interval: int = 5
    ) -> List[Dict]:
        """
        Scrape reviews from multiple restaurants
        
        Args:
            restaurants: List of restaurant dictionaries with keys:
                - 'url': Google Maps URL
                - 'name': Restaurant name
                - 'neighborhood': Neighborhood name
                - 'cuisine_type': Type of cuisine (optional)
            reviews_per_restaurant: Max reviews per restaurant
            delay_between_requests: (min, max) seconds to wait between requests
            save_interval: Save progress every N restaurants
        
        Returns:
            List of all reviews
        """
        total_restaurants = len(restaurants)
        logger.info("#" * 60)
        logger.info(f"Starting batch scrape of {total_restaurants} restaurants")
        logger.info(f"Target: ~{total_restaurants * reviews_per_restaurant} reviews")
        logger.info("#" * 60)
        
        successful_scrapes = 0
        failed_scrapes = 0
        
        for i, restaurant in enumerate(restaurants):
            logger.info(f"[{i+1}/{total_restaurants}] Processing restaurant...")
            
            reviews = self.scrape_restaurant_reviews(
                place_url=restaurant['url'],
                restaurant_name=restaurant['name'],
                neighborhood=restaurant['neighborhood'],
                cuisine_type=restaurant.get('cuisine_type', 'Unknown'),
                max_reviews=reviews_per_restaurant,
                sort_by="newest"
            )
            
            if reviews:
                successful_scrapes += 1
            else:
                failed_scrapes += 1
                logger.warning(f"No reviews collected from {restaurant['name']}")
            
            # Save progress at intervals
            if (i + 1) % save_interval == 0:
                self.save_to_csv(f"reviews_progress_{i+1}.csv")
                logger.info(f"Progress saved: {successful_scrapes} successful, {failed_scrapes} failed")
            
            # Random delay to be respectful to API
            if i < total_restaurants - 1:
                delay = random.uniform(*delay_between_requests)
                logger.info(f"Waiting {delay:.1f} seconds before next restaurant...")
                time.sleep(delay)
        
        logger.info("#" * 60)
        logger.info("SCRAPING COMPLETE")
        logger.info(f"Total reviews collected: {len(self.all_reviews)}")
        logger.info(f"Successful restaurants: {successful_scrapes}/{total_restaurants}")
        logger.info(f"Failed restaurants: {failed_scrapes}/{total_restaurants}")
        logger.info("#" * 60)
        
        return self.all_reviews
    
    def save_to_csv(self, filename: str = "manhattan_reviews.csv"):
        """Save all reviews to CSV"""
        if self.all_reviews:
            df = pd.DataFrame(self.all_reviews)
            df.to_csv(filename, index=False, encoding='utf-8')
            logger.info(f"Saved {len(self.all_reviews)} reviews to {filename}")
        else:
            logger.warning("No reviews to save")
    
    def save_to_json(self, filename: str = "manhattan_reviews.json"):
        """Save all reviews to JSON"""
        if self.all_reviews:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.all_reviews, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(self.all_reviews)} reviews to {filename}")
        else:
            logger.warning("No reviews to save")
    
    def get_summary_stats(self) -> Optional[pd.DataFrame]:
        """Generate summary statistics"""
        if not self.all_reviews:
            logger.warning("No reviews collected yet")
            return None
        
        df = pd.DataFrame(self.all_reviews)
        
        logger.info("=" * 60)
        logger.info("SUMMARY STATISTICS")
        logger.info("=" * 60)
        logger.info(f"Total reviews: {len(df)}")
        logger.info(f"\nReviews by neighborhood:")
        logger.info(f"\n{df['neighborhood'].value_counts()}")
        logger.info(f"\nReviews by cuisine:")
        logger.info(f"\n{df['cuisine_type'].value_counts()}")
        
        # Handle potential None values in rating
        valid_ratings = df['rating'].dropna()
        if len(valid_ratings) > 0:
            logger.info(f"\nAverage rating: {valid_ratings.mean():.2f}")
        else:
            logger.warning("\nNo valid ratings found")
            
        logger.info(f"Average review length: {df['review_length'].mean():.1f} characters")
        logger.info(f"Reviews with owner response: {df['owner_response'].notna().sum()} ({df['owner_response'].notna().sum()/len(df)*100:.1f}%)")
        logger.info(f"Local guide reviews: {df['is_local_guide'].sum()} ({df['is_local_guide'].sum()/len(df)*100:.1f}%)")
        
        return df


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == "__main__":
    
    # STEP 1: Add your 4 Apify API tokens here
    # Get tokens from: https://console.apify.com/account/integrations
    API_TOKENS = [
        "apify_api_YOUR_TOKEN_1_HERE",  # Account 1
        "apify_api_YOUR_TOKEN_2_HERE",  # Account 2
        "apify_api_YOUR_TOKEN_3_HERE",  # Account 3
        "apify_api_YOUR_TOKEN_4_HERE",  # Account 4
    ]
    
    # STEP 2: Define your restaurants
    # Find URLs by going to Google Maps, searching for restaurants,
    # clicking on them, and copying the URL from your browser
    
    # restaurants are in three files (each for different neighborhoods) in rest_data folder. 
    restaurant_files = ["high_income.json", "mid_income.json", "low_income.json"]
    restaurants = []
    for file in restaurant_files:
        with open(os.path.join("rest_data", file), 'r', encoding='utf-8') as f:
            data = json.load(f)
            restaurants.extend(data)

    logger.info(f"Loaded {len(restaurants)} restaurants from {len(restaurant_files)} files")
    
    # STEP 3: Initialize scraper with your tokens
    scraper = ApifyMultiAccountScraper(
        API_TOKENS,
        max_retries=3  # Retry failed requests up to 3 times
    )
    
    # STEP 4: Run the scraper
    # Target: ~50 restaurants x 50 reviews each = 2,500 reviews
    try:
        reviews = scraper.scrape_multiple_restaurants(
            restaurants=restaurants,
            reviews_per_restaurant=50,  # Adjust based on needs
            delay_between_requests=(3, 7),  # Random delay 3-7 seconds
            save_interval=5  # Save progress every 5 restaurants
        )
        
        # STEP 5: Save final results
        scraper.save_to_csv("manhattan_reviews_final.csv")
        scraper.save_to_json("manhattan_reviews_final.json")
        
        # STEP 6: View summary
        df = scraper.get_summary_stats()
        
        # STEP 7: Optional - Show sample reviews
        if df is not None and len(df) > 0:
            logger.info("=" * 60)
            logger.info("SAMPLE REVIEWS BY NEIGHBORHOOD")
            logger.info("=" * 60)
            for neighborhood in df['neighborhood'].unique():
                logger.info(f"\n{neighborhood}:")
                sample = df[df['neighborhood'] == neighborhood].head(2)
                for idx, row in sample.iterrows():
                    rating_display = f"{row['rating']}" if pd.notna(row['rating']) else "N/A"
                    logger.info(f"  Rating: {rating_display} - {row['restaurant_name']}")
                    review_preview = row['review_text'][:100] if row['review_text'] else "(No text)"
                    logger.info(f"    '{review_preview}...'")
                    
    except Exception as e:
        logger.error(f"Fatal error during scraping: {e}")
        logger.info("Attempting to save any collected data...")
        scraper.save_to_csv("manhattan_reviews_emergency_save.csv")
        raise