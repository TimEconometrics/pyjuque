from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import sqlalchemy as db
from datetime import datetime
from decimal import Decimal
import sqlalchemy.types as types
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import backref
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
Base = declarative_base()

def get_session(path='sqlite:///'):
    some_engine = create_engine(path, echo=False)
    Base.metadata.create_all(some_engine)
    Session = sessionmaker(bind=some_engine)
    session = Session()
    return session
    
class SqliteDecimal(types.TypeDecorator):
	# This TypeDecorator use Sqlalchemy Integer as impl. It converts Decimals
	# from Python to Integers which is later stored in Sqlite database.
	impl = types.BigInteger

	def __init__(self, scale):
		# It takes a 'scale' parameter, which specifies the number of digits
		# to the right of the decimal point of the number in the column.
		types.TypeDecorator.__init__(self)
		self.scale = scale
		self.multiplier_int = 10 ** self.scale

	def process_bind_param(self, value, dialect):
		# e.g. value = Column(SqliteDecimal(2)) means a value such as
		# Decimal('12.34') will be converted to 1234 in Sqlite
		if value is not None:
			value = int(Decimal(value) * self.multiplier_int)
		return value

	def process_result_value(self, value, dialect):
		# e.g. Integer 1234 in Sqlite will be converted to SqliteDecimal('12.34'),
		# when query takes place.
		if value is not None:
			value = Decimal(value) / self.multiplier_int
		return value


class Bot(Base):
    """ 
        I removed some things form here, check that it works with everything you did
    """
    __tablename__ = 'bot'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30))
    is_running = db.Column(db.Boolean, default=False)
    test_run = db.Column(db.Boolean, default=False)
    quote_asset = db.Column(db.String(10), index=True)
    starting_balance = db.Column(SqliteDecimal(13))
    current_balance = db.Column(SqliteDecimal(13))
    profit_loss = db.Column(db.Float, default=100)
    entry_settings_id = db.Column(db.Integer, ForeignKey('entry_settings.id'))
    exit_settings_id = db.Column(db.Integer, ForeignKey('exit_settings.id'))

    def getPairs(self, session):
            return session.query(Pair).filter_by(bot_id=self.id).all()

    def getActivePairs(self, session):
            return session.query(Pair).filter_by(bot_id=self.id, active=True).all()

    def getPairWithSymbol(self, session, symbol):
            return session.query(Pair).filter_by(bot_id=self.id, symbol=symbol).first()

    def getOrders(self, session):
            return session.query(Order).filter_by(bot_id=self.id).all()

    def getOpenOrders(self, session):
            return session.query(Order).filter_by(bot_id=self.id, is_closed=False).all()    

class EntrySettings(Base):
    """ Entry Settings of a Bot """
    __tablename__ = 'entry_settings'
    id = db.Column(db.Integer, primary_key=True)                  	# Unique ID
    name = db.Column(db.String(30))                                 # Name (for UI)
    bots = relationship('Bot', backref=backref('entry_settings'))
    initial_entry_allocation = db.Column(db.Integer, default=None)	# What % of funds allocated to the bot will go                                                                 # to an initial entry
    subsequent_entries = db.Column(db.Integer, default=0)         	# Are there subsequent entries
    subsequent_entry_allocation = db.Column(db.Float, default=1)  	# What % of the initial quantity will we buy on a 
                                                                    # subsequent entry (1 = 100%, 0.5 = 50%)
    subsequent_entry_distance = db.Column(db.Float, default=None) 	# Distance between subsequent entries in %
    signal_distance = db.Column(db.Float, default=None)         		# Distance from signal for initial entry 
                                                                        # None means enter on signal, 1 means enter 1% away 
                                                                        # - in the direction opposite that of the trade - 
                                                                        # from the signal price

class ExitSettings(Base):
    """ Exit Settings of a Bot """
    __tablename__ = 'exit_settings'
    id = db.Column(db.Integer, primary_key=True)                  	# Unique ID
    name = db.Column(db.String(30))                               	# Name for UI
    bots = relationship('Bot', backref=backref('exit_settings'))   # Name (for UI)
    profit_target = db.Column(db.Float)                           	# Exit when price is at value % profit from entry 
    stop_loss_value = db.Column(db.Float, default=None)             	# Whether to have stop loss or not (and what %)
    is_trailing_stop_loss = db.Column(db.Boolean, default=False)    	# Whether to have trailing stop loss or not (what %)
    stop_loss_active_after = db.Column(db.Float, default=None)    	# If we have trailing stop loss, whether to activate 
                                                                    # immediately, or after a value % increase in profit

if __name__ == "__main__":
    session = get_session()
    bot = Bot(name='Tim', id=12)
    session.add(bot)
    e = EntrySettings(id =1, name ='Time')
    ex = ExitSettings(id = 1, name ='Tim')
    bot.entry_settings = e
    bot.exit_settings = ex
    session.commit()

    bot_v1 = session.query(Bot).filter_by(id=12).first()
    print(bot_v1.entry_settings)

