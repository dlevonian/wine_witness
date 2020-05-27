<h1>Wine Witness: a data-driven approach to item promotion at Vivino</h1>
    

<p>If you ever had to make up your mind staring at dozens of similarly priced bottles of Californian Cabernet in a wine store, or if you wanted to learn more about the wine you just tried when travelling, then you probably know of <a href="https://www.vivino.com">Vivino</a>.&nbsp;</p>
<p>It’s the SoundHound of wines. Just take a picture of the label, and Vivino <span style="font-weight: 400">will match it to one of the 1+ billion label photos in its database and then deliver all its basic information. </span></p>



<figure class="wp-block-image size-large"><img srcset='https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-691842-uy7SXkDb-300x152.png 300w, https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-691842-uy7SXkDb.png 423w' sizes='(max-width: 423px) 100vw, 423px' src="https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-691842-uy7SXkDb.png" alt="" class="wp-image-61920" /></figure>



<p>Launched in 2010 in Denmark by Heini Zachariassen (check out his youtube <a href="https://www.youtube.com/channel/UCHiSUe3Bo5cRMhE6BjttNUA">channel</a>), it quickly built a massive community of users ranging from casual drinkers to wine experts. Today Vivino has 43 million registered users who rate wines, write reviews and like each other’s posts.</p>
<p>In 2017, Vivino decided to capitalize on their vast network and launched a wine marketplace, where wineries and merchants register to sell their wines. Tens of thousands of wine items are sold on Vivino globally, with about 14,400 available when accessing from the U.S. East Coast. This is a typical picture on the front page:</p>



<figure class="wp-block-image size-large"><img srcset='https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-744660-rQDPVxWc-300x128.png 300w, https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-744660-rQDPVxWc.png 571w' sizes='(max-width: 571px) 100vw, 571px' src="https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-744660-rQDPVxWc.png" alt="" class="wp-image-61922" /></figure>



<p>With so many wines listed by the merchants, the question for Vivino is, which ones are good deals?</p>
<p>If there is a way to estimate the ‘true’ price of the wine, Vivino could signal to its loyal customers that some wines are priced much below their value.  And there are many reasons why a good wine may be offered at a discount: it may be a promotion by the merchant, a liquidation of stock, or sometimes just an oversupply from a good vintage year.</p>
<p>But can Vivino quickly identify the fair price range of a bottle without having to rely entirely on manual verification?</p>



<h3><strong>Exploring the data</strong></h3>



<p>An important number to remember when scraping dynamic websites with Selenium is 86,400. That’s the number of seconds per day. Selenium spent about 4-5 seconds navigating each wine page, which means a hard cap of only 20,000 samples per day. For many machine learning applications, this is a [very] small dataset.</p>
<p>With that said, Vivino had only 14,400 items currently selling in the U.S., so all of them got scraped. For each wine, 13 key characteristics were obtained:</p>



<figure class="wp-block-image size-large"><img srcset='https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-755562-uoRxy6ir-300x82.png 300w, https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-755562-uoRxy6ir.png 467w' sizes='(max-width: 467px) 100vw, 467px' src="https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-755562-uoRxy6ir.png" alt="" class="wp-image-61930" /></figure>



<p>We first explore the data visually to verify if the price is correlated with any of the features. As we can see, prices have 67% correlation with the average rating – wines with higher ratings are usually more expensive. &nbsp;There is also a slightly negative correlation with the <em>number</em> of ratings, and the relationship resembles the typical inverse price/quantity curve.</p>
<p>However, there is still lots of variability. One great 4.2-star wine can be priced at $20 and another at $200! A lot of variability in the wine prices comes from <em>perceived </em>quality, as opposed to any objective characteristics. This variability may be explained by other predictors such as expert reviews or social media mentions and probably has a good deal of irreducible, natural variation.</p><div class='mailmunch-forms-in-post-middle' style='display: none !important;'></div>



<figure class="wp-block-image size-large"><img srcset='https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-346460-2FLcO2s0-300x300.png 300w, https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-346460-2FLcO2s0.png 419w' sizes='(max-width: 419px) 100vw, 419px' src="https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-346460-2FLcO2s0.png" alt="" class="wp-image-61932" /></figure>



<p>Wine styles and countries of origin clearly have explanatory power, with medians ranging from $20-25 &nbsp;to $60-80.&nbsp; These are clearly good predictors of price:</p>



<figure class="wp-block-image size-large"><img srcset='https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-231072-nNzMmZX1-300x137.png 300w, https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-231072-nNzMmZX1.png 536w' sizes='(max-width: 536px) 100vw, 536px' src="https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-231072-nNzMmZX1.png" alt="" class="wp-image-61927" /></figure>



<p>However, we should be cautious and resist the temptation of throwing all the features into the model. This may lead to overfitting and reduce the predictive power on out-of-sample, previously unseen data.</p>
<p>For example, the specific winery and the vintage certainly influence the price but we had to remove them from the predictive features b/c they were too granular (less than 3 wine items per winery).</p>



<h3>Modelling the price</h3>



<p>We built a few simple models to capture the relationship between the features and the price. Because the relationship is complex and highly non-linear, a one-layer fully-connected neural network showed the best results both in-sample and out-of-sample.&nbsp; Ordinary least squares is shown here merely as benchmark; you would not expect it to work well with numerous categorical features and a modest dataset.</p>



<figure class="wp-block-image size-large"><img srcset='https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-766493-cRXZCzTS-300x84.png 300w, https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-766493-cRXZCzTS.png 501w' sizes='(max-width: 501px) 100vw, 501px' src="https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-766493-cRXZCzTS.png" alt="" class="wp-image-62477" /></figure>



<p>The model can predict the price with Mean Absolute Error of about $10 and R<sup>2</sup> of about 75%. The percentage price difference is distributed quasi-normally, so we can infer that the model probably has extracted all useful information there was in our limited scraped features.</p>
<p>For our practical purposes, the most interesting part of this curve is on the right side, where our model thinks about 10% of the items must be priced at least 50% higher than the current listed price at Vivino. These are the candidates to be promoted as great deals!</p>



<figure class="wp-block-image size-large"><img srcset='https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-119454-7bpwN7Ko-300x139.png 300w, https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-119454-7bpwN7Ko.png 493w' sizes='(max-width: 493px) 100vw, 493px' src="https://nycdsa-blog-files.s3.us-east-2.amazonaws.com/2020/05/dmitri-levonian/image-119454-7bpwN7Ko.png" alt="" class="wp-image-61933" /></figure>



<p>For a quick reference on converting categorical features (e.g. 1,149 wine-producing regions) into machine-learnable format, selecting the feature subsets and comparing models' performance, please see the project's <a href="https://github.com/dlevonian/wine_witness">github</a>.</p>



<h3>Conclusions</h3>



<p>We built a model that explains about 75% of variability in the wine prices, and for about 10% of the items, the model predicts a 1.5x higher price than the actual one.&nbsp; The system could flag such items automatically and pass it for human verification.&nbsp; Such AI-aided marketing may prove to be another way to build customer loyalty and curate Vivino’s relationships with the wineries and merchants.</p>
<p>Probably the most promising direction to improve predictions is analyzing reviews, and typical Vivino wines have thousands of them. As in any online marketplace, the hive mind is usually well-informed. An NLP engine could extract sentiment from these reviews and make our price predictions more precise.</p>
<p>On a more general note, Vivino seems to have the ambition of becoming the Amazon of wine. To succeed in the growing $300 b global wine industry with less than 5% share of online sales, Vivino will need to reinvent itself as <em>data</em> <em>company</em> much the same way Amazon has done. &nbsp;</p>
