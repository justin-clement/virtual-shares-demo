
# Decorator function to handle errors.
def safe_run(func):
	def wrapper(*args, **kwargs):
		try:
			result = func(*args, **kwargs)
			return result
		except Exception as e:
			print("\n")
			error_message = {'status': False, 'message': f'An exception occured ({e})'}
			print(error_message)   # In production, this will be passed to the error log.
		    return error_message
	return wrapper

# Decorator function to demarcate transaction printouts.
def line(func):
	def wrapper(*args, **kwargs):
		print("\n")
		func(*args, **kwargs)
		print("\n                ---------------------------------------")
	return wrapper


class VirtualShares:

	"""
	The three values below would be stored in a database during production.
	For this model, once this class is initialized, it keeps track of
	both free shares and bought shares.
	"""
	total_shares = (1000000,)      # Let's say we have 1 million shares. This is stored in a tuple for immutability.
	free_shares = total_shares[0] 
	bought_shares = 0            

	@safe_run
	def __init__(self, owner_id: str, shares: float):
		self.owner_id = owner_id

		if shares >= VirtualShares.total_shares[0] or shares >= VirtualShares.free_shares or shares <= 0:
			raise ValueError(f" Unable to create account for {self.owner_id}. The given amount of shares are not available to own.")
		else:
			self.__shares = shares
			VirtualShares.bought_shares += shares
			VirtualShares.free_shares -= shares
			print(f"Shareholder account created: Owner ID: {self.owner_id} || Shares: {self.__shares}")

	@classmethod
	def overview(cls):
		"""See all shares."""
		print(f"\n TOTAL VIRTUAL SHARES: {cls.total_shares[0]} \n FREE: {cls.free_shares} \n BOUGHT: {cls.bought_shares}") 	


	# The following are user-oriented methods. 

	@safe_run
	def display_owner_info(self):
		print(f" {self.owner_id} owns {self.__shares} virtual shares.")

	@safe_run
	@line
	def direct_purchase(self, number_of_shares: float):
		"""Purchase shares from Service directly, if available."""
		initial_shares = self.__shares

		if VirtualShares.free_shares <= 0:
			return print(" There are no available shares at the moment. Kindly check back later or consider buying from a user.")
		if number_of_shares > (VirtualShares.free_shares or VirtualShares.total_shares) or number_of_shares <= 0:
			return print(" The requested amount of shares are not available.")

		updated_free_shares = VirtualShares.free_shares - number_of_shares
		updated_bought_shares = VirtualShares.bought_shares + number_of_shares
		VirtualShares.free_shares = updated_free_shares
		VirtualShares.bought_shares = updated_bought_shares
		new_shares = initial_shares + number_of_shares
		self.__shares = new_shares

		# In production, these can be logged into a journal or ledger. Or a text file acting as one.
		print(f"\n PURCHASE OF {number_of_shares} VIRTUAL SHARES FROM SERVICE BY {self.owner_id} SUCCESSFUL.")
		print(f" Previous volume of shares held by {self.owner_id}: {initial_shares} \n Current volume: {self.__shares}")
		return {'status': True, 'message': f'direct purchase of shares from Service by {self.owner_id} successful'}
	
	# The Sell function should be a private method. 	
	@safe_run
	def __sell(self, number_of_shares: float, buyer: object):
		"""Initiate a sell transaction by a client (after agreement to sell)."""

		if number_of_shares > self.__shares or number_of_shares <= 0:
			print(f"\n SALE OF {number_of_shares} SHARES FROM {self.owner_id} TO {buyer.owner_id} UNSUCCESSFUL.")
			return {'status': False, 'message': 'insufficient volume of shares to sell'}
		else: 
			initial_shares = self.__shares
			new_shares = initial_shares - number_of_shares
			self.__shares = new_shares

			# In production, these can be logged into a journal or ledger. Or a text file acting as one.
			print(f"\n SALE OF {number_of_shares} VIRTUAL SHARES BY {self.owner_id} TO {buyer.owner_id} SUCCESSFUL.")
			print(f" Previous volume of shares held by {self.owner_id}: {initial_shares} \n Current volume: {new_shares}")
			return {'status': True, 'message': f'sale of shares from {self.owner_id} to {buyer.owner_id} successful'}

	# This is the method used to call the Sell function.
	@safe_run
	def process_sell(self, number_of_shares: float, buyer: object):
		return self.__sell(number_of_shares, buyer)

	@safe_run
	@line
	def peer_purchase(self, number_of_shares: float, seller: object):
		"""Purchase shares from another user."""

		if number_of_shares <= 0:
			raise ValueError(" Shares to buy must be more than zero.")

		initial_shares = self.__shares
		seller_action = seller.process_sell(number_of_shares, self)
		if not seller_action['status']:
			print(" Transaction could not be completed. Please try again later.")
			return {'status': False, 
					'message': f"transaction could not be completed by seller ({seller_action['message']})"}
		else:
			new_shares = initial_shares + number_of_shares
			self.__shares = new_shares

			# In production, these can be logged into a journal or ledger. Or a text file acting as one.
			print(f"\n PURCHASE OF {number_of_shares} VIRTUAL SHARES FROM {seller.owner_id} BY {self.owner_id} SUCCESSFUL.")
			print(f" Previous volume of shares held by {self.owner_id}: {initial_shares} \n Current volume: {self.__shares}")
			return {'status': True, 'message': f'purchase from {seller.owner_id} to {self.owner_id} successful'}
