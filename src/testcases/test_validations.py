import datetime
import pytest
import app


@pytest.mark.parametrize("value,expected", [(7, (7, False)), ('7', (7, False))])
def test_validate_store_id_success(value, expected):
    result = app.validate_store_id(value)
    assert expected == result


@pytest.mark.parametrize("value,expected", [('a', 'Store IDs should be integers.'),
                                            ('7.5', 'Store IDs should be integers.')])
def test_validate_store_id_failure(value, expected):
    result = app.validate_store_id(value)
    assert expected == result[1]


@pytest.mark.parametrize("value,expected", [('Apple', False), ('orange', False)])
def test_validate_product_name_success(value, expected):
    result = app.validate_product_name(value)
    assert expected == result


@pytest.mark.parametrize("value,expected", [('Apple1', 'Invalid Product Name'), ('123456', 'Invalid Product Name')])
def test_validate_product_name_failure(value, expected):
    result = app.validate_product_name(value)
    assert expected == result


@pytest.mark.parametrize("value,expected", [('2022-04-03', datetime.date(year=2022, month=4, day=3)),
                                            ('1993-04-06', datetime.date(year=1993, month=4, day=6))])
def test_validate_date_success(value, expected):
    result = app.validate_date(value)
    assert expected == result[0]


@pytest.mark.parametrize("value,expected", [('2022/04/03', 'Invalid Date'),
                                            ('03-04-2022', 'Invalid Date')])
def test_validate_date_failure(value, expected):
    result = app.validate_date(value)
    assert expected == result[1]


@pytest.mark.parametrize("value,expected", [('0.12', 0.12),
                                            ('20', 20),
                                            (0.456, 0.456)])
def test_validate_price_success(value, expected):
    result = app.validate_price(value)
    assert expected == result[0]


@pytest.mark.parametrize("value,expected", [('0.1a2', 'Invalid Price'),
                                            ('ab', 'Invalid Price')])
def test_validate_price_failure(value, expected):
    result = app.validate_price(value)
    assert expected == result[1]


@pytest.mark.parametrize("values,expected", [({'Store ID': '2',
                                               'Product Name': 'Apple',
                                               'Date': '2022-04-02',
                                               'Price': '0.45'},
                                              {'Store ID': 2,
                                               'Product Name': 'Apple',
                                               'Date': datetime.date(year=2022, month=4, day=2),
                                               'Price': 0.45}),
                                             ])
def test_validate_price_feed_success(values, expected):

    app.validate_price_feed(values)
    assert expected == values


@pytest.mark.parametrize("values,expected", [({'Store ID': '2',
                                               'Product Name': 'Apple1',
                                               'Date': '2022-04-02',
                                               'Price': '0.45'},
                                              'Invalid Product Name'),
                                             ])
def test_validate_price_feed_failure(values, expected):

    result = app.validate_price_feed(values)
    assert expected == result[1]