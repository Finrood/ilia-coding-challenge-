# ilia-coding-challenge

## Performance test results

In this section, we'll compare the performances between the original version of the code and my improvements.
#### Original Code Performance

<img width="595" alt="perf-test-default-code" src="https://github.com/Finrood/ilia-coding-challenge/assets/66259833/8eba1db9-9586-4731-8c49-ea8ba762f0f0">

#### Improved Code Performance (Without Product Deletion and Order List)

![perf-test-changed-code-default-test](https://github.com/Finrood/ilia-coding-challenge/assets/66259833/9476c0c7-f016-4773-9d4a-ebba857ab44b)


#### Improved Code Performance (With Product Deletion)

![perf-test-without-list-orders](https://github.com/Finrood/ilia-coding-challenge/assets/66259833/503359a1-7b46-48f5-83c1-34e066a155b2)

#### Improved Code Performance (With Product Deletion and Order List)

![perf-test-with-list-orders](https://github.com/Finrood/ilia-coding-challenge/assets/66259833/1e1e3614-7860-4785-8a16-6b797da569fa)


## Analysis
#### Question 1: Why is performance degrading as the test run longer?
Before my changes, the performance was degrading over time. Upon investigation, I found that when getting an `order`, we were fetching ALL the `products` and filtering them afterward. As the number of products grew, this call took longer.


_PS: 
I first thought the problem might be cause my missing indexes in the database. I then added indexes in `order_details` on `order_id` (here, explicitely declaring the index on the foreign key because even though most database automatically create an index on foreign keys, some do not) and i also added a index on `product_id`. While not used in our cases, I still added it because we might want to do some filtering on that field in the future._

_After **adding those indexes**, I noticed that **no performance gain were made**, meaning that our database created a index on the foreign key automatically. So after looking a bit more, **I found that when getting an `order`, we would fetch ALL the `products` and filter on them afterward.** Of course, as the number of products grew, the longer this call was taking.__


#### Question 2: How do you fix it?
**_I fixed it by getting the `product` we wanted directly instead of loading the whole list and filtering afterward_**

Additionally, it's worth noting that we observed performance degradation when the performance test included order listing. This is due to the increasing number of orders in the database over time. Implementing paging would be a good idea if we expect it to grow significantly.
